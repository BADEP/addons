# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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
from collections import OrderedDict
from openerp import models, fields, api, tools, SUPERUSER_ID
from openerp.addons.product import _common
from openerp.osv import osv
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    qty_invoiced = fields.Float(digits_compute=dp.get_precision('Product Unit of Measure'), compute='get_invoiced_data', store=True, string='Quantité facturée',)
    qty_delivered = fields.Float(digits_compute=dp.get_precision('Product Unit of Measure'), compute='get_delivered_data', store=True, string='Quantité livrée',)
    qty_to_invoice = fields.Float(digits_compute=dp.get_precision('Product Unit of Measure'), compute='get_to_invoice_data', store=True, string='Quantité à facturer',)
    amount_delivered = fields.Float(string='Montant livré', digits=dp.get_precision('Account'), store=True, readonly=True, compute='get_delivered_data', track_visibility='always')
    amount_invoiced = fields.Float(string='Montant facturé', digits=dp.get_precision('Account'), store=True, readonly=True, compute='get_invoiced_data', track_visibility='always')
    amount_to_invoice = fields.Float(string='Montant à facturer', digits=dp.get_precision('Account'), store=True, readonly=True, compute='get_to_invoice_data', track_visibility='always')
    price_unit = fields.Float(string='Unit Price', required=True, digits_compute= dp.get_precision('Product Price'), readonly=True, states={'draft': [('readonly', False)]}, group_operator='avg')
    warehouse = fields.Many2one('stock.warehouse', related='order_id.warehouse_id',string='Entrepôt', store=True)
    salesteam = fields.Many2one('crm.case.section', related='order_id.section_id', string='Equipe commerciale', store=True)
    fiscal_position = fields.Many2one('account.fiscal.position', related='order_id.fiscal_position', string='Position Fiscale', store=True)
    last_price_base = fields.Float(string='Dernier prix de base', digits_compute= dp.get_precision('Product Price'), readonly=True)
    last_cost_unit = fields.Float(string='Dernier prix DT', digits_compute= dp.get_precision('Product Price'), readonly=True)
    last_price_unit = fields.Float(string='Dernier prix', digits_compute= dp.get_precision('Product Price'), readonly=True)
    
    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):
        res = super(SaleOrderLine, self).product_id_change(pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag)
        
        lines = self.search([('order_id', '!=', self.order_id.id), ('order_partner_id', '=', partner_id), ('product_id', '=', product)], order='create_date DESC')
        res['value'].update({'last_price_base': lines and lines[0].price_base or False,
                             'last_cost_unit': lines and lines[0].cost_unit or False,
                             'last_price_unit': lines and lines[0].price_unit or False})
        return res
    
    @api.one
    @api.depends('invoice_lines')
    def get_invoiced_data(self):
        qty = 0
        amount = 0
        cur = self.order_id.pricelist_id.currency_id
        uom = self.product_uos or self.product_uom
        for line in self.invoice_lines:
            if line.invoice_id.state in ('open', 'done', 'paid'):
                qty += self.env['product.uom']._compute_qty_obj(line.uos_id, line.quantity, uom)
                amount += line.price_total
        self.qty_invoiced = qty
        self.amount_invoiced = cur.round(amount)
        

    @api.one
    @api.depends('move_ids')
    def get_delivered_data(self):
        delivered = 0
        cur = self.order_id.pricelist_id.currency_id
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        for move in self.move_ids:
            if move.state == 'done':
                if move.location_dest_id.usage == 'customer':
                    delivered += self.env['product.uom']._compute_qty_obj(move.product_uom, move.product_uom_qty, self.product_uom)
                if move.location_id.usage == 'customer':
                    delivered -= self.env['product.uom']._compute_qty_obj(move.product_uom, move.product_uom_qty, self.product_uom)
        self.qty_delivered = delivered
        amount = self.tax_id.compute_all(price, self.qty_delivered, self.product_id, self.order_id.partner_id)
        self.amount_delivered = cur.round(amount['total_included'])

    @api.one
    @api.depends('qty_delivered','qty_invoiced')
    def get_to_invoice_data(self):
        self.qty_to_invoice = self.qty_delivered - self.qty_invoiced
        cur = self.order_id.pricelist_id.currency_id
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        amount = self.tax_id.compute_all(price, self.qty_to_invoice, self.product_id, self.order_id.partner_id)
        self.amount_to_invoice = cur.round(amount['total_included'])
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
