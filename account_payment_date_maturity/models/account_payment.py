# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    date_maturity = fields.Date(string="Due Date")

    def _prepare_payment_moves(self):
        res = super(AccountPayment, self)._prepare_payment_moves()
        for move_val in res:
            for move_line_val in move_val['line_ids']:
                move_line_val[2].update({
                    'date_maturity': self.date_maturity if self.date_maturity and move_line_val[2]['debit'] else self.payment_date
                })
        return res
