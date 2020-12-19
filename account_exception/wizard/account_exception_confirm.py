# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# Copyright 2020 BADEP
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountExceptionConfirm(models.TransientModel):
    _name = 'account.exception.confirm'
    _inherit = ['exception.rule.confirm']

    related_model_id = fields.Many2one('account.invoice', 'Invoice')

    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.ignore_exception = True
        return super().action_confirm()
