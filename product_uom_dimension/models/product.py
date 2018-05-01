# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class ProductUom(models.Model):
    _inherit = "product.uom"
    
    @api.one
    def _get_default_label(self):
        return self.name
    
    label = fields.Char(required=True, default=_get_default_label)
    dimensions = fields.One2many('product.uom.dimension', 'product_uom', copy=True)
    formula = fields.Char(required=True)

class ProductUomDimension(models.Model):
    _name = 'product.uom.dimension'
    name = fields.Char(required=True)

    product_uom = fields.Many2one('product.uom', required=True)
