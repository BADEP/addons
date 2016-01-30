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

class product_uom(models.Model):
    _inherit = "product.uom"
    dimensions = fields.One2many('product.uom.dimension', 'product_uom', copy=True)

product_uom()

class product_uom_dimension(models.Model):
    _name = 'product.uom.dimension'
    name = fields.Char(required=True)
    multiplier = fields.Float(string='Coeff.', required=True, digits_compute=dp.get_precision('Product UoS'), default=1)
    rounding = fields.Float(string='Palier', digits_compute=dp.get_precision('Product UoS'), required=False)
    offset = fields.Float(string='biais', required=True, digits_compute=dp.get_precision('Product UoS'), default=0)
    product_uom = fields.Many2one('product.uom', required=True)
    
product_uom_dimension()