from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_registry = fields.Char(string='RC')
    pat = fields.Char(string='Patente')
    cnss = fields.Char(string='CNSS')
    idf = fields.Char(string='IF')