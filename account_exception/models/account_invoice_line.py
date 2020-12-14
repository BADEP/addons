# © 2019 Akretion
# Copyright 2020 BADEP
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = ['account.invoice.line', 'base.exception.method']
    _name = 'account.invoice.line'

    ignore_exception = fields.Boolean(
        related='invoice_id.ignore_exception',
        store=True,
        string="Ignore Exceptions")

    @api.multi
    def _get_main_records(self):
        return self.mapped('invoice_id')

    @api.model
    def _reverse_field(self):
        return 'invoice_ids'

    @api.multi
    def _detect_exceptions(self, rule):
        records = super(AccountInvoiceLine, self)._detect_exceptions(rule)
        return records.mapped('invoice_id')

    @api.model
    def _exception_rule_eval_context(self, rec):
        # We keep this only for backward compatibility, because some existing
        # rules may use the variable "sale_line". But we should remove this
        # code during v13 migration. The record is already available in obj and
        # object variables and it is more than enough.
        res = super(AccountInvoiceLine, self)._exception_rule_eval_context(rec)
        res['invoice_line'] = rec
        return res
