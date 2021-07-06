from odoo import fields,models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    to_measure = fields.Boolean(string='Articles à mesurer', default=False)