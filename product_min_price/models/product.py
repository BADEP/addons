# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    purchase_min_price = fields.Float(string='Purchase price', compute='_get_min_purchase_price', digits=dp.get_precision('Product Price'))

    @api.one
    @api.depends('seller_ids')
    def _get_min_purchase_price(self):
        seller_price = self.seller_ids.filtered(lambda s: (not s.date_start or s.date_start < fields.Datetime.now()) and
                                                          (not s.date_end or s.date_end > fields.Datetime.now())).mapped('price')
        self.purchase_min_price = seller_price and min(seller_price) or 0

class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_min_price = fields.Float(string='Purchase price', compute='_get_min_purchase_price', digits=dp.get_precision('Product Price'))

    @api.one
    @api.depends('seller_ids')
    def _get_min_purchase_price(self):
        seller_price = self.variant_seller_ids.filtered(lambda s: (not s.product_id or s.product_id == self) and
                                                                  (not s.date_start or s.date_start < fields.Date.today()) and
                                                                  (not s.date_end or s.date_end > fields.Date.today())).mapped('price')
        self.purchase_min_price = seller_price and min(seller_price) or 0
