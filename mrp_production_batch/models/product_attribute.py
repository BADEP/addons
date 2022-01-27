from odoo import models, fields, api

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    group_in_mrp_batch = fields.Boolean(string='Group in MRP Batches', default=True)