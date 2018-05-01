# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class PosCategory(models.Model):
    _inherit = "pos.category"
    
    color = fields.Char('Couleur', help="The table's color, expressed as a valid 'background' CSS property value")
    
class ProductProduct(models.Model):
    _inherit = "product.product"
    
    color = fields.Char('Couleur', related='pos_categ_id.color')