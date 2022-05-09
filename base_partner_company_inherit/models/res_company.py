from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'
    _inherits = {'res.partner': 'partner_id'}
    _name = 'res.company'