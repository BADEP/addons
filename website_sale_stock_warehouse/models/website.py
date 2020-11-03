# -*- coding: utf-8 -*-
from odoo import api, models, fields

class Website(models.Model):
    _inherit = 'website'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

    @api.multi
    def _prepare_sale_order_values(self, partner, pricelist):
        self.ensure_one()
        values = super(Website, self)._prepare_sale_order_values(partner, pricelist)
        if self.warehouse_id:
            values['warehouse_id'] = self.warehouse_id.id
        return values

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    warehouse_id = fields.Many2one('stock.warehouse', related='website_id.warehouse_id', string='Warehouse', readonly=False)
