# -*- coding: utf-8 -*-
from odoo import models, fields
    
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    pat = fields.Char(string='Patente')
    ice = fields.Char(string='ICE')
    cnss = fields.Char(string='CNSS')

