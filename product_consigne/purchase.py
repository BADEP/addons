# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 BADEP. All Rights Reserved.
#    Author: Khalid Hazam<k.hazam@badep.ma>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _prepare_inv_bundle_line(self, cr, uid, account_id, order_line, item, context=None):
        """Collects require data from purchase order line that is used to create invoice line
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        return {
            'name': item.item_id.name,
            'account_id': account_id,
            'price_unit': item.item_id.standard_price or 0.0,
            'quantity': order_line.product_qty * item.qty_uom,
            'product_id': item.item_id.id or False,
            'uos_id': item.uom_id.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in item.item_id.supplier_taxes_id])],
            'account_analytic_id': order_line.account_analytic_id.id or False,
            'purchase_line_id': order_line.id,
        }

    def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        context = dict(context or {})
        
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        inv2_obj = self.pool.get('account.invoice')
        inv2_line_obj = self.pool.get('account.invoice.line')

        res = False
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        for order in self.browse(cr, uid, ids, context=context):
            context.pop('force_company', None)
            if order.company_id.id != uid_company_id:
                # if the company of the document is different than the current user company, force the company in the context
                # then re-do a browse to read the property fields for the good company.
                context['force_company'] = order.company_id.id
                order = self.browse(cr, uid, order.id, context=context)
            
            # generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
            inv_lines = []
            inv2_lines = []
            for po_line in order.order_line:
                if po_line.product_id.bundle == True:
                    for item in po_line.product_id.item_ids:
                        if item.item_id.container == True:
                            acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                            inv2_line_data = self._prepare_inv_bundle_line(cr, uid, acc_id, po_line, item, context=context)
                            inv2_line_id = inv2_line_obj.create(cr, uid, inv2_line_data, context=context)
                            inv2_lines.append(inv2_line_id)
                            po_line.write({'invoice_lines': [(4, inv2_line_id)]})
                        else:
                            acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                            inv_line_data = self._prepare_inv_bundle_line(cr, uid, acc_id, po_line, item, context=context)
                            inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                            inv_lines.append(inv_line_id)
                            po_line.write({'invoice_lines': [(4, inv_line_id)]})
                else:
                    if po_line.product_id.container == True:
                        acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                        inv2_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
                        inv2_line_id = inv2_line_obj.create(cr, uid, inv2_line_data, context=context)
                        inv2_lines.append(inv2_line_id)
                        po_line.write({'invoice_lines': [(4, inv2_line_id)]})
                    else:
                        acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                        inv_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
                        inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                        inv_lines.append(inv_line_id)
                        po_line.write({'invoice_lines': [(4, inv_line_id)]})

            # get invoice data and create invoice
            inv_data = self._prepare_invoice(cr, uid, order, inv_lines, context=context)
            inv_data.update({'inv_type': 'product'})
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)
            inv2_data = self._prepare_invoice(cr, uid, order, inv2_lines, context=context)
            inv2_data.update({'inv_type': 'consigne'})
            inv2_id = inv_obj.create(cr, uid, inv2_data, context=context)
            # compute the invoice
            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)
            inv2_obj.button_compute(cr, uid, [inv2_id], context=context, set_total=True)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)]})
            order.write({'invoice_ids': [(4, inv2_id)]})
            res = inv_id
        return res

purchase_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

