from odoo import models, fields, api

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    debit = fields.Monetary(currency_field='currency_id', compute='_get_debit_credit', inverse='_set_debit_amount', store=True, readonly=False)
    credit = fields.Monetary(currency_field='currency_id', compute='_get_debit_credit', inverse='_set_credit_amount', store=True, readonly=False)

    @api.depends('amount')
    def _get_debit_credit(self):
        for line in self:
            line.credit = max(line.amount, 0)
            line.debit = max(-line.amount, 0)

    @api.onchange('debit')
    def _set_debit_amount(self):
        for line in self.filtered(lambda l: l.debit):
            line.credit = 0
            line.amount = -line.debit

    @api.onchange('credit')
    def _set_credit_amount(self):
        for line in self.filtered(lambda l: l.credit):
            line.debit = 0
            line.amount = line.credit