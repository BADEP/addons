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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class procurement_order(models.Model):
    _inherit = "procurement.order"
    dimensions = fields.One2many('procurement.order.dimension', 'procurement_order')
    product_dimension_qty = fields.Integer('Quantité', required=True, default=0)
    
    @api.model
    def _prepare_mo_vals(self, procurement):
        res = super(procurement_order, self)._prepare_mo_vals(procurement)
        res['product_dimension_qty'] = procurement.product_dimension_qty
        res['dimensions'] = [(0, 0, {'dimension': x.dimension.id, 'quantity': x.quantity}) for x in procurement.dimensions]
        return res
    
    @api.model
    def _run_move_create(self, procurement):
        res = super(procurement_order, self)._run_move_create(procurement)
        res['product_dimension_qty'] = procurement.product_dimension_qty
        res['dimensions'] = [(0, 0, {'dimension': x.dimension.id, 'quantity': x.quantity}) for x in procurement.dimensions]
        return res
        
procurement_order()

class procurement_order_dimension(models.Model):
    _name = "procurement.order.dimension"
    dimension = fields.Many2one('product.uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', digits_compute=dp.get_precision('Product UoS'), required=True)
    procurement_order = fields.Many2one('procurement.order', required=True, ondelete='cascade')
    extrapolated_qty = fields.Integer(string='Quantité extrapolée', compute='get_extrapolated_qty')
    
    @api.one
    @api.depends('dimension', 'quantity')
    def get_extrapolated_qty(self):
        if self.dimension.rounding!=0:
            self.extrapolated_qty = round(self.quantity / self.dimension.rounding)
        else:
            self.extrapolated_qty = self.quantity + self.dimension.offset
    
procurement_order_dimension()

class stock_move(models.Model):
    _inherit = 'stock.move'
    dimensions = fields.One2many('stock.move.dimension', 'stock_move')
    product_dimension_qty = fields.Integer('Quantité', required=True, default=0)

    @api.model
    def _prepare_procurement_from_move(self, move):
        res = super(stock_move, self)._prepare_procurement_from_move(move)
        res['product_dimension_qty'] = move.product_dimension_qty
        res['dimensions'] = [(0, 0, {'dimension': x.dimension.id, 'quantity': x.quantity}) for x in move.dimensions]
        return res
stock_move()

class stock_move_dimension(models.Model):
    _name = "stock.move.dimension"
    
    dimension = fields.Many2one('product.uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', digits_compute=dp.get_precision('Product UoS'), required=True)
    stock_move = fields.Many2one('stock.move', required=True, ondelete='cascade')
    extrapolated_qty = fields.Integer(string='Quantité extrapolée', compute='get_extrapolated_qty')
    
    @api.one
    @api.depends('dimension', 'quantity')
    def get_extrapolated_qty(self):
        if self.dimension.rounding!=0:
            self.extrapolated_qty = round(self.quantity / self.dimension.rounding)
        else:
            self.extrapolated_qty = self.quantity + self.dimension.offset

stock_move_dimension()