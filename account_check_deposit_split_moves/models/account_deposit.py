# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (http://www.akretion.com/)
# @author: Benoît GUILLOT <benoit.guillot@akretion.com>
# @author: Chafique DELLI <chafique.delli@akretion.com>
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# @author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class AccountCheckDeposit(models.Model):
    _inherit = "account.check.deposit"

    @api.multi
    def validate_deposit(self):
        am_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        for deposit in self:
            move_vals = self._prepare_account_move_vals(deposit)
            move = am_obj.create(move_vals)
            total_debit = 0.0
            total_amount_currency = 0.0
            to_reconcile_lines = []
            for line in deposit.check_payment_ids:
                total_debit += line.debit
                total_amount_currency += line.amount_currency
                line_vals = self._prepare_move_line_vals(line)
                line_vals['move_id'] = move.id
                move_line = move_line_obj.with_context(
                    check_move_validity=False).create(line_vals)
                to_reconcile_lines.append(line + move_line)
                counter_vals = self._prepare_counterpart_move_lines_vals(
                                                                         deposit, line.debit, line.amount_currency)
                counter_vals['name'] = _('Check Deposit - Ref. Check %s') % line.ref
                counter_vals['move_id'] = move.id
                move_line_obj.create(counter_vals)
            if deposit.company_id.check_deposit_post_move:
                move.post()

            deposit.write({'state': 'done', 'move_id': move.id})
            for reconcile_lines in to_reconcile_lines:
                reconcile_lines.reconcile()
        return True
