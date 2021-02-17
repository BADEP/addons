# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
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

from odoo import fields, models
import odoo.addons.decimal_precision as dp


class product_template(models.Model):
    _inherit = 'product.template'
    
    delivery_costs = fields.One2many('product.delivery.cost', 'product', string="Coûts de livraison")

class product_delivery_cost(models.Model):
    _name = 'product.delivery.cost'
    _description = 'Coût de livraison'
    code = fields.Many2one('product.delivery.code', ondelete='cascade', string='Tarif DT')
    price = fields.Float(required=True, digits_compute=dp.get_precision('Product Price'), default=0, string='Prix transport')
    product = fields.Many2one('product.template', ondelete='cascade', string='Article')
    pricelist = fields.Many2one('product.pricelist', ondelete='set null')

class product_delivery_code(models.Model):
    _name = 'product.delivery.code'
    _description = 'Tarif DT'

    name = fields.Char(required=True, string='Label')
    partners = fields.One2many('res.partner', 'code', string='Clients')
    delivery_costs = fields.One2many('product.delivery.cost', 'code', string='DT')

