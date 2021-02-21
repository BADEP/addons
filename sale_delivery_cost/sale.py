# -*- coding: utf-8 -*-

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class sale_order_line_old(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(sale_order_line_old, self).product_id_change()
        if self.product_id:
            cost = 0
            for delivery_cost in self.product_id.product_tmpl_id.delivery_costs:
                    cost += delivery_cost.price
            self.price_base =  self.price_unit
            self.price_unit =  self.price_unit + cost
        return res

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    cost_subtotal = fields.Float(required=True, digits_compute=dp.get_precision('Account'), default=0, compute='get_cost_subtotal', string='Total DT')
    cost_unit = fields.Float(required=True, digits_compute=dp.get_precision('Account'), default=0, string='DT unitaire')
    price_base = fields.Float(required=True, digits_compute=dp.get_precision('Account'), default=0, string='Prix de base')

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

class sale_order(models.Model):
    _inherit = 'sale.order'
    delivery_cost = fields.Float(digits_compute=dp.get_precision('Account'), compute='get_delivery_cost', string='Total DT')
    code = fields.Many2one('product.delivery.code', string='Tarif DT')
    
    @api.depends('order_line')
    def get_delivery_cost(self):
        cost = 0
        for line in self.order_line:
            cost += line.cost_subtotal
        self.delivery_cost = cost
    
    def onchange_delivery_id(self, company_id, partner_id, delivery_id, fiscal_position):
        r = super(sale_order, self).onchange_delivery_id(company_id, partner_id, delivery_id, fiscal_position)
        delivery = self.env['res.partner'].browse(delivery_id)
        r['value']['code'] = delivery.code and delivery.code.id or False
        return r

    def action_ship_create(self):
        res = super(sale_order, self).action_ship_create()
        vals = {
                'code': self.code and self.code.id or False,
                }
        self.picking_ids.write(vals)
        return res

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    code = fields.Many2one('product.delivery.code', string='Tarif DT')
