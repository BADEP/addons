from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    user_type_id = fields.Many2one('account.journal.type', string='Sous-Type', inverse='_inverse_user_type', required=False)

    def _inverse_user_type(self):
        for rec in self:
            rec.type = rec.user_type_id.type