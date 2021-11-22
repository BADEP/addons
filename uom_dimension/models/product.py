from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    custom_uom_code = fields.Char(string='Custom code for UoM calculation')