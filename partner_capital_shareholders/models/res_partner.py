from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    part_ids = fields.One2many('res.partner.part', 'parent_partner_id', string='Shareholders Parts')
    stake_ids = fields.One2many('res.partner.part', 'partner_id', string='Shareholder Stakes')

class ResPartnerPart(models.Model):
    _name = 'res.partner.part'

    partner_id = fields.Many2one('res.partner', string='Shareholder', required=True, ondelete='cascade')
    parent_partner_id = fields.Many2one('res.partner', string='Company', required=True, ondelete='cascade')
    part = fields.Float(string='Part', required=True)