# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ['stock.picking', 'tier.validation']
    _state_from = ['assigned', 'waiting', 'confirmed']
    _state_to = ['done']

    def button_validate(self):
        self.write({'state': 'done'})
        return super().button_validate()

    def _notify_accepted_reviews(self):
        return super(StockPicking, self.sudo())._notify_accepted_reviews()
