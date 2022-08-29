from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    part_ids = fields.One2many('res.partner.part', 'parent_partner_id', string='Shareholders Parts')
    stake_ids = fields.One2many('res.partner.part', 'partner_id', string='Shareholder Stakes')

class ResPartnerPart(models.Model):
    _name = 'res.partner.part'
    _description = 'Partner Part'
    _order = 'parent_partner_id,part'

    partner_id = fields.Many2one('res.partner', string='Shareholder', required=True, ondelete='cascade')
    parent_partner_id = fields.Many2one('res.partner', string='Company', required=True, ondelete='cascade')
    part = fields.Float(string='Parts', required=True, digits=(16, 5))
    part_amount = fields.Float(string='Part Amount', compute = '_part_amount')
    part_percent = fields.Float(string='Part %', compute = '_part_amount', digits=(16, 2))
    type = fields.Selection([('internal', 'Interne'), ('external', 'Externe')])
    display_name = fields.Char(compute='_display_name')

    @api.depends('partner_id', 'part_percent')
    def _display_name(self):
        for rec in self:
            rec.display_name = '%s%%: %s' % (round(rec.part_percent, 2), rec.partner_id.name)

    @api.depends('part', 'parent_partner_id.capital_amount', 'parent_partner_id.part_ids', 'parent_partner_id.part_ids.part')
    def _part_amount(self):
        for rec in self:
            all_parts = sum(rec.parent_partner_id.part_ids.mapped('part'))
            rec.part_amount = 0 if all_parts == 0 else (rec.parent_partner_id.capital_amount * rec.part / all_parts)
            rec.part_percent = 0 if all_parts == 0 else (100 * rec.part / all_parts)