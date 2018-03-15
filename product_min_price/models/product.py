# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    purchase_min_price = fields.Float(string='Prix d\'achat minimum', compute='_get_min_price', digits=dp.get_precision('Product Price'))

    @api.one
    @api.depends('seller_ids')
    def _get_min_price(self):
        if self.seller_ids:
            self.purchase_min_price = min(self.seller_ids.mapped('price'))