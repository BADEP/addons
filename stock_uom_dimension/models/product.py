from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_dimensions_strict = fields.Boolean(string='Isoler les dimensions dans l\'inventaire')