from odoo import models, fields, api

class AccountJournalType(models.Model):
    _name = 'account.journal.type'
    _description = 'User-defined Journal type'

    active = fields.Boolean(default=True)
    name = fields.Char(string='Account Type', required=True, translate=True)
    type = fields.Selection([
            ('sale', 'Ventes'),
            ('purchase', 'Achats'),
            ('cash', 'Espèces'),
            ('bank', 'Banque'),
            ('general', 'Divers'),
        ], required=True)
    journal_ids = fields.One2many('account.journal', 'user_type_id', string='Journals')
    journal_count = fields.Integer(string='# Of Journals', compute='_journal_count')

    @api.depends('journal_ids')
    def _journal_count(self):
        for rec in self:
            rec.journal_count = len(rec.journal_ids)

    def action_view_journals(self):
        pass