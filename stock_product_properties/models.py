# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, exceptions, _
from openerp.addons import decimal_precision as dp

class StockMoveProperty(models.Model):
    _name = 'stock.move.property'
    
    property = fields.Many2one('product.property', domain="[('id', 'in', possible_properties[0][2])]", string='Propriété')
    value = fields.Char(required = True, string='Valeur')
    move = fields.Many2one('stock.move', string='Mouvement')
    possible_properties = fields.Many2many(
        comodel_name='product.property',
        compute='_get_possible_properties', readonly=True)

    @api.one
    @api.depends('move.properties', 'move.product_id', 'move.product_id.properties')
    def _get_possible_properties(self):
        possible_properties = self.env['product.property']
        for property in self.move.product_id.properties:
                possible_properties |= property
        self.possible_properties = possible_properties.sorted()

class StockMove(models.Model):
    _inherit = 'stock.move'
    properties = fields.One2many('stock.move.property', 'move')

class ProductProperty(models.Model):
    _name = 'product.property'
    
    name = fields.Char(string='Nom', required = True)
    products = fields.Many2many('product.product', string='Articles')
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    properties = fields.Many2many('product.property', string='Propriétés')