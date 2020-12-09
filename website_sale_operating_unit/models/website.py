# -*- coding: utf-8 -*-
from odoo import api, models, fields

class Website(models.Model):
    _inherit = 'website'

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')

    @api.multi
    def _prepare_sale_order_values(self, partner, pricelist):
        self.ensure_one()
        values = super(Website, self)._prepare_sale_order_values(partner, pricelist)
        if self.operating_unit_id:
            values['operating_unit_id'] = self.operating_unit_id.id
        return values

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    operating_unit_id = fields.Many2one('operating.unit', related='website_id.operating_unit_id', string='Operating Unit', readonly=False)
