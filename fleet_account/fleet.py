# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 BADEP (<http://badep.ma>).
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

from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta

def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class fleet_vehicle_cost(osv.Model):
    _inherit = 'fleet.vehicle.cost'
    
    
    def _invoiced(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for cost in self.browse(cr, uid, ids, context=context):
            res[cost.id] = True if cost.invoice_id else False
        return res
    _columns = {
        'invoiced': fields.function(_invoiced, string='Invoice Received', type='boolean', copy=False,
                                    help="It indicates that an invoice has been validated"),
        'state': fields.selection([('draft', 'Draft'), ('progress','Confirmed'), ('cancel','Cancelled')],
                                  'Status', readonly=True, copy=False),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True, copy=False),
        
    }

    _defaults ={
        'invoiced': False,
        'state': 'draft'
    }
    
    def action_invoice_create(self, cr, uid, ids, supplier_id,context=None):
        context = dict(context or {})
        
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        supplier = self.pool.get('res.partner').browse(cr, uid, supplier_id, context=context)
        inv_lines=[]
        origin =''
        for cost in self.browse(cr,uid,ids, context=context):
            if cost.invoiced == False:
                inv_line_data = {
                    'name': cost.name,
                    'account_id': cost.cost_subtype_id.product_id.property_account_expense or cost.cost_subtype_id.product_id.categ_id.property_account_expense_categ.id,
                    'price_unit': cost.amount or 0.0,
                    'quantity': 1,
                    'product_id': cost.cost_subtype_id.product_id.id or False,
                    'uos_id': cost.cost_subtype_id.product_id.uom_po_id.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in cost.cost_subtype_id.product_id.supplier_taxes_id])],
                }
                origin = origin + ',' + cost.name
                inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                inv_lines.append(inv_line_id)
        journal_ids = self.pool['account.journal'].search(
                    cr, uid, [('type', '=', 'purchase'),
                              ('company_id', '=', uid_company_id.id)],
                    limit=1)
        if not journal_ids:
            raise osv.except_osv(
                _('Error!'),
                _('Define purchase journal for this company: "%s" (id:%d).') % \
                    (uid_company_id.name, uid_company_id.id))
            
        inv_data =  {
            'name': supplier.ref or supplier.name,
            'reference': supplier.ref or supplier.name,
            'account_id': supplier.property_account_payable.id,
            'type': 'in_invoice',
            'partner_id': supplier.id,
            'currency_id': uid_company_id.currency_id.id,
            'journal_id': len(journal_ids) and journal_ids[0] or False,
            'invoice_line': [(6, 0, inv_lines)],
            'origin': origin,
            'fiscal_position': supplier.property_account_position.id or False,
            'payment_term': supplier.property_supplier_payment_term.id or False,
            'company_id': uid_company_id.id,
        }
        inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # compute the invoice
        inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)

            # Link this new invoice to related purchase order
        for cost in self.browse(cr,uid,ids, context=context):
            if cost.invoiced == False:
                cost.write({'invoice_id': inv_id})
                cost.write({'invoiced': True})
    
class fleet_service_type(osv.Model):
    _inherit = 'fleet.service.type'
    _columns = {
        'product_id': fields.many2one('product.product', 'Invoicable Product'),
    }
    
class fleet_vehicle_log_services(osv.Model):
    _inherit = 'fleet.vehicle.log.services'
    
    def action_invoice_create(self, cr, uid, ids, supplier_id=None,context=None): 
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        inv_lines=[]
        journal_ids = self.pool['account.journal'].search(
                    cr, uid, [('type', '=', 'purchase'),
                              ('company_id', '=', uid_company_id.id)],
                    limit=1)
        if not journal_ids:
            raise osv.except_osv(
                _('Error!'),
                _('Define purchase journal for this company: "%s" (id:%d).') % \
                    (uid_company_id.name, uid_company_id.id))
        for service in self.browse(cr,uid,ids, context=context):
            supplier_id=service.vendor_id.id
            if not supplier_id:
                raise osv.except_osv(
                                     _('Error!'),
                                     _('No supplier defined'))
                context = dict(context or {})
            if service.invoiced == False:
                for cost in service.cost_ids:
                    inv_line_data = {
                        'name': cost.name,
                        'account_id': cost.cost_subtype_id.product_id.property_account_expense or cost.cost_subtype_id.product_id.categ_id.property_account_expense_categ.id,
                        'price_unit': cost.amount or 0.0,
                        'quantity': 1,
                        'product_id': cost.cost_subtype_id.product_id.id or False,
                        'uos_id': cost.cost_subtype_id.product_id.uom_po_id.id or False,
                        'invoice_line_tax_id': [(6, 0, [x.id for x in cost.cost_subtype_id.product_id.supplier_taxes_id])],
                    }
                    inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                    inv_lines.append(inv_line_id)
        
                if inv_lines:
                    inv_data =  {
                        'name': service.vendor_id.ref or service.vendor_id.name,
                        'reference': service.vendor_id.ref or service.vendor_id.name,
                        'account_id': service.vendor_id.property_account_payable.id,
                        'type': 'in_invoice',
                        'partner_id': service.vendor_id.id,
                        'currency_id': uid_company_id.currency_id.id,
                        'journal_id': len(journal_ids) and journal_ids[0] or False,
                        'invoice_line': [(6, 0, inv_lines)],
                        'origin': service.name,
                        'fiscal_position': service.vendor_id.property_account_position.id or False,
                        'payment_term': service.vendor_id.property_supplier_payment_term.id or False,
                        'company_id': uid_company_id.id,
                    }
                    inv_id = inv_obj.create(cr, uid, inv_data, context=context)
            
                        # compute the invoice
                    inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)
                    
                    service.write({'invoice_id': inv_id})
                    service.write({'invoiced': True})
                    for cost in service.cost_ids: 
                        cost.write({'invoice_id': inv_id})
                        cost.write({'invoiced': True})
        return True
    
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for service in self.browse(cr,uid,ids,context):
            amount = 0
            for cost in service.cost_ids:
                amount += cost.amount
            res[service.id]=amount
        return res
    
    
    _columns = {
        'amount': fields.function(_amount, string='Amount', type='float'),
    }