# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    date_maturity = fields.Date(string="Due Date")
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res = super()._prepare_move_line_default_vals(write_off_line_vals)
        for line in res:
            line.update({'date_maturity': self.date_maturity})
        return res

    # def write(self, vals):
    #     if not vals.get('date'):
    #         vals.update({'date': self.date})
    #     res = super().write(vals)
    #     return res

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    date_maturity = fields.Date(string="Due Date")

    def _create_payment_vals_from_wizard(self):
        res = super()._create_payment_vals_from_wizard()
        res.update({'date_maturity': self.date_maturity})
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super()._create_payment_vals_from_batch()
        res.update({'date_maturity': self.date_maturity})
        return res