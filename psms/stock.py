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


class stock_location_pump(models.Model):
    _name = 'stock.location.pump'
    
    location = fields.Many2one('stock.location', required=True, ondelete='cascade', string="Emplacement", domain=[('usage', '=', 'internal'), ('active', '=', True)])
    counter = fields.Float(digits_compute=dp.get_precision('Product UoS'), required=True, default=0, string="Compteur")
    name = fields.Char(string="Nom")
    product = fields.Many2one('product.product', ondelete='set null', string="Article")
    logs = fields.One2many('sale.session.log', 'pump')
    electric_diff = fields.Float(digits_compute=dp.get_precision('Product UoS'), required=True, default=0, string="Décalage électrique")
    electric_counter = fields.Float(digits_compute=dp.get_precision('Product UoS'), compute='get_electric_counter', string="Compteur électrique")
    
    @api.depends('counter', 'electric_diff')
    @api.one
    def get_electric_counter(self):
        self.electric_counter = self.counter + self.electric_diff
    
stock_location_pump()

class product_product(models.Model):
    _inherit = 'product.product'
    
    pumps = fields.One2many('stock.location.pump', 'product', string="Pompes")
    session_lines = fields.One2many('sale.session.line', 'product', string="Lignes de carburant")
product_product()
