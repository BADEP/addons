from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    part_ids = fields.One2many('res.partner.part', 'parent_partner_id', string='Shareholders Parts')
    stake_ids = fields.One2many('res.partner.part', 'partner_id', string='Shareholder Stakes')

class ResPartnerPart(models.Model):
    _name = 'res.partner.part'

    partner_id = fields.Many2one('res.partner', string='Shareholder', required=True, ondelete='cascade')
    parent_partner_id = fields.Many2one('res.partner', string='Company', required=True, ondelete='cascade')
    part = fields.Float(string='Parts', required=True)
    part_amount = fields.Float(string='Part Amount', compute = '_part_amount')
    type = fields.Selection([('internal', 'Interne'), ('external', 'Externe')])

    @api.depends('part', 'parent_partner_id.capital_amount', 'parent_partner_id.part_ids', 'parent_partner_id.part_ids.part')
    def _part_amount(self):
        for rec in self:
            all_parts = sum(rec.parent_partner_id.part_ids.mapped('part'))
            rec.part_amount = 0 if all_parts == 0 else (rec.parent_partner_id.capital_amount * rec.part / all_parts)