from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    part_ids = fields.One2many('res.partner.part', related='partner_id.part_ids', string='Shareholders Parts')
