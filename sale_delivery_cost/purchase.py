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

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    cost_subtotal = fields.Float(required=True, digits_compute=dp.get_precision('Account'), default=0, compute='get_cost_subtotal', string='Total DT')
    cost_unit = fields.Float(required=True, digits_compute=dp.get_precision('Account'), default=0, string='DT unitaire')
    price_base = fields.Float(required=True, digits_compute=dp.get_precision('Account'), default=0, string='Prix de base')

    @api.one
    @api.depends('cost_unit', 'product_qty')
    def get_cost_subtotal(self):
        self.cost_subtotal = self.cost_unit * self.product_qty

    @api.onchange('cost_unit')
    def onchane_cost_unit(self):
        self.price_unit = self.price_base + self.cost_unit
    
    @api.onchange('price_unit')
    def onchane_price_unit(self):
        self.price_base = self.price_unit - self.cost_unit

    @api.onchange('price_base')
    def onchane_price_base(self):
        self.price_unit = self.cost_unit + self.price_base


class purchase_order(models.Model):
    _inherit = 'purchase.order'
    delivery_cost = fields.Float(digits_compute=dp.get_precision('Account'), compute='get_delivery_cost', string='Total DT')
    
    @api.depends('order_line')
    def get_delivery_cost(self):
        cost = 0
        for line in self.order_line:
            cost += line.cost_subtotal
        self.delivery_cost = cost
