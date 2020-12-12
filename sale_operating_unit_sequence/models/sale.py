# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'operating_unit_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(operating_unit_id=vals['operating_unit_id']).next_by_code(
                    'sale.order') or _('New')
        return super().create(vals)