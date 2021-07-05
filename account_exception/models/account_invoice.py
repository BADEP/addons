# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# Copyright 2020 BADEP
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    model = fields.Selection(
        selection_add=[
            ('account.invoice', 'Invoice'),
            ('account.invoice.line', 'Invoice Line'),
        ]
    )
    invoice_ids = fields.Many2many(
        'account.invoice',
        string="Invoices")


class AccountInvoice(models.Model):
    _inherit = ['account.invoice', 'base.exception']
    _name = 'account.invoice'

    @api.model
    def _exception_rule_eval_context(self, rec):
        res = super(AccountInvoice, self)._exception_rule_eval_context(rec)
        res['invoice'] = rec
        return res

    @api.model
    def _reverse_field(self):
        return 'invoice_ids'

    def detect_exceptions(self):
        all_exceptions = super(AccountInvoice, self).detect_exceptions()
        lines = self.mapped('invoice_line_ids')
        all_exceptions += lines.detect_exceptions()
        return all_exceptions

    @api.model
    def test_all_draft_invoices(self):
        invoice_set = self.search([('state', '=', 'draft')])
        invoice_set.detect_exceptions()
        return True

    def _fields_trigger_check_exception(self):
        return ['ignore_exception', 'invoice_line_ids', 'state']

    @api.model
    def create(self, vals):
        record = super(AccountInvoice, self).create(vals)
        check_exceptions = any(
            field in vals for field
            in self._fields_trigger_check_exception()
        )
        if check_exceptions:
            record.invoice_check_exception()
        return record

    def write(self, vals):
        result = super(AccountInvoice, self).write(vals)
        check_exceptions = any(
            field in vals for field
            in self._fields_trigger_check_exception()
        )
        if check_exceptions:
            self.invoice_check_exception()
        return result

    def invoice_check_exception(self):
        invoices = self.filtered(lambda i: i.state in ('open', 'paid'))
        if invoices:
            invoices._check_exception()

    @api.onchange('invoice_line_ids')
    def onchange_ignore_exception(self):
        if self.state in ('open', 'paid'):
            self.ignore_exception = False

    def action_invoice_open(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        return super().action_invoice_open()

    def action_invoice_draft(self):
        res = super().action_invoice_draft()
        invoices = self.filtered(lambda i: i.ignore_exception)
        invoices.write({
            'ignore_exception': False,
        })
        return res

    # def _sale_get_lines(self):
    #     self.ensure_one()
    #     return self.order_line

    @api.model
    def _get_popup_action(self):
        return self.env.ref('account_exception.action_account_exception_confirm')
