# -*- coding: utf-8 -*-

from odoo import models

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom):
        res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom)
        res.update({
            'dimension_ids': values.get('dimension_ids', [])
        })
        return res

