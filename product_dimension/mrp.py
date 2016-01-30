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


class mrp_production(models.Model):
    _inherit = "mrp.production"
    dimensions = fields.One2many('mrp.production.dimension','mrp_production')
    product_dimension_qty = fields.Integer('Quantité', required=True, default=0)
    dimensions_label = fields.Char('Qté. produite', compute='get_dimensions_label')
    sale_dimensions_label = fields.Char('Description', compute='get_sale_dimensions_label')
    
    @api.one
    def get_dimensions_label(self):
        str_dim = (str(self.product_dimension_qty) + ' - ') if self.product_dimension_qty != 0 else ''
        for d in self.dimensions:
            str_dim += str(d.extrapolated_qty) + '*'
        str_dim = str_dim[:-1]
        self.dimensions_label = str_dim

    @api.one
    def get_sale_dimensions_label(self):
        if self.dimensions:
            str_dim = (str(self.product_dimension_qty) if self.product_dimension_qty != 0 else '') + ' ' + self.product_id.name + ' '
            for d in self.dimensions:
                str_dim += str(d.quantity) + '*'
            str_dim = str_dim[:-1]
            self.sale_dimensions_label = str_dim
        else:
            self.sale_dimensions_label = self.product_id.name
    
mrp_production()

class mrp_production_dimension(models.Model):
    _name = "mrp.production.dimension"
    dimension = fields.Many2one('product.uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', digits_compute= dp.get_precision('Product UoS'), required=True)
    mrp_production = fields.Many2one('mrp.production', required=True, ondelete='cascade')
    extrapolated_qty = fields.Integer(string='Quantité extrapolée', compute='get_extrapolated_qty')
    
    @api.one
    @api.depends('dimension', 'quantity')
    def get_extrapolated_qty(self):
        if self.dimension.rounding!=0:
            self.extrapolated_qty = round(self.quantity / self.dimension.rounding)
        else:
            self.extrapolated_qty = self.quantity + self.dimension.offset
mrp_production_dimension()