# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2016-2016 BADEP. All Rights Reserved.
#    Author: Khalid HAZAM <k.hazam@badep.ma>
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
from openerp.osv import fields as oldfields, osv
from openerp import tools
from openerp import fields, models, api
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    taxes_on_margin = fields.Boolean(string='Taxes sur Marge', default=False)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.cr_uid_context
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        line_obj = self.pool['sale.order.line']
        price = line_obj._calc_line_base_price(cr, uid, line, context=context) - (line.purchase_price if line.taxes_on_margin else 0)
        qty = line_obj._calc_line_quantity(cr, uid, line, context=context)
        for c in self.pool['account.tax'].compute_all(
                cr, uid, line.tax_id, price, qty, line.product_id,
                line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    taxes_on_margin = fields.Boolean(string='Taxes sur Marge')
    
    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):
        ctx = self.env.context.copy()
        product_obj = self.env['product.product'].browse(product)
        result = super(SaleOrderLine, self.with_context(ctx)).product_id_change(pricelist, product, qty, uom, qty_uos, uos, name,
                                        partner_id, lang, update_tax, date_order, packaging,
                                        fiscal_position, flag)
        result['value'].update({'taxes_on_margin': product_obj.taxes_on_margin})
        return result

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    taxes_on_margin = fields.Boolean(string='Taxes sur Marge')
    
    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        result = super(AccountInvoiceLine, self).product_id_change(product, uom_id, qty, name, type,
            partner_id, fposition_id, price_unit, currency_id,
            company_id)
        result['value'].update({'taxes_on_margin': product.taxes_on_margin})
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
