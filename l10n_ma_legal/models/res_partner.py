# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    rc = fields.Char(string='RC')
    pat = fields.Char(string='Patente')
    idf = fields.Char(string='IF')
    ice = fields.Char(string='ICE')
