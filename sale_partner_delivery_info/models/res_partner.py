# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    warehouse_id = fields.Many2one('stock.warehouse', u'Entrepôt par défaut')
    
