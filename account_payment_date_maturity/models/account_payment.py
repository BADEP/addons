# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    date_maturity = fields.Date(string="Maturity Date")

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        res = super(AccountPayment, self)._get_shared_move_line_vals(debit, credit, amount_currency, move_id, invoice_id=invoice_id)
        res.update({
            'date_maturity': self.date_maturity if self.date_maturity else self.payment_date
        })
        return res
