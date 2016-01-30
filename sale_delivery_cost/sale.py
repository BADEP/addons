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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from openerp.osv import osv, fields as oldfields


class sale_order_line_old(osv.osv):
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line_old, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        cost = 0
        
        product_obj = self.pool.get('product.product').browse(cr, uid, product, context)
        partner_shipping_id = self.pool.get('res.partner').browse(cr, uid, context.get('partner_shipping_id'), context)
        for delivery_cost in product_obj.product_tmpl_id.delivery_costs:
            if delivery_cost.code.id == partner_shipping_id.code.id:
                cost += delivery_cost.price
                break
        if 'price_unit' in res['value']:
            res['value'].update({'price_base': res['value']['price_unit']})
            res['value'].update({'price_unit': res['value']['price_unit'] + cost})
        return res

sale_order_line_old()

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    cost_subtotal = fields.Float(required=True, digits_compute=dp.get_precision('Account'), default=0, compute='get_cost_subtotal', string='Total DT')
    cost_unit = fields.Float(required=True, digits_compute=dp.get_precision('Account'), default=0, string='DT unitaire')
    price_base = fields.Float(required=True, digits_compute=dp.get_precision('Account'), default=0, string='Prix de base')

    @api.one
    @api.depends('cost_unit', 'product_uom_qty')
    def get_cost_subtotal(self):
        self.cost_subtotal = self.cost_unit * self.product_uom_qty

    @api.onchange('cost_unit')
    def onchane_cost_unit(self):
        self.price_unit = self.price_base + self.cost_unit
    
    @api.onchange('price_unit')
    def onchane_price_unit(self):
        self.cost_unit = self.price_unit - self.price_base

    @api.onchange('price_base')
    def onchane_price_base(self):
        self.price_unit = self.cost_unit + self.price_base
sale_order_line()

class sale_order(models.Model):
    _inherit = 'sale.order'
    vehicle = fields.Many2one('fleet.vehicle', readonly=True, states={'draft': [('readonly', False)]}, string='Véhicule')
    driver = fields.Many2one('res.partner', related='vehicle.driver_id', store=True, readonly=True, states={'draft': [('readonly', False)]}, string='Chauffeur')
    driver_cost = fields.Float(digits_compute=dp.get_precision('Account'), default=0, string='Coût transport')
    delivery_cost = fields.Float(digits_compute=dp.get_precision('Account'), compute='get_delivery_cost', string='Total DT')
    
    @api.depends('order_line')
    def get_delivery_cost(self):
        cost = 0
        for line in self.order_line:
            cost += line.cost_subtotal
        self.delivery_cost = cost
    
    @api.one
    def action_ship_create(self):
        res = super(sale_order, self).action_ship_create()
        vals = {
                'vehicle': self.vehicle.id,
                'driver': self.driver.id,
                'driver_cost': self.driver_cost
                }
        self.picking_ids.write(vals)
        return res
sale_order()

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    vehicle = fields.Many2one('fleet.vehicle', readonly=False, states={'done': [('readonly', True)]}, string='Véhicule')
    driver = fields.Many2one('res.partner', readonly=False, states={'done': [('readonly', True)]}, string='Chauffeur')
    driver_cost = fields.Float(digits_compute=dp.get_precision('Account'), default=0, string='Coût transport')
    
stock_picking()
