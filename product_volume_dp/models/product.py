from odoo import models, fields
from odoo.addons import decimal_precision as dp

class ProductProduct(models.Model):
    _inherit = 'product.product'

    volume = fields.Float('Volume', help="The volume in m3.", digits=dp.get_precision('Volume'))

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    volume = fields.Float(
        'Volume', compute='_compute_volume', inverse='_set_volume',
        help="The volume in m3.", digits=dp.get_precision('Volume'), store=True)