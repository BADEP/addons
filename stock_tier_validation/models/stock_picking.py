# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ['stock.picking', 'tier.validation']
    _state_from = ['assigned', 'waiting', 'confirmed']
    _state_to = ['done']

    def action_done(self):
        self.write({'state': 'done'})
        res = super().action_done()
        return res

    def _notify_accepted_reviews(self):
        return super(StockPicking, self.sudo())._notify_accepted_reviews()

    def button_validate(self):
        if not self.validated and self.need_validation and not self.review_ids:
            self.request_validation()
        else:
            # return super(StockPicking, self).button_validate()
            return super(StockPicking, self.with_context(needs_validation=True)).button_validate()
