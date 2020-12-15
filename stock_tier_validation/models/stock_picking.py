# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ['stock.picking', 'tier.validation']
    _state_from = ['assigned', 'waiting', 'confirmed']
    _state_to = ['done']
