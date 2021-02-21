# -*- coding: utf-8 -*-

from odoo import fields, models


class res_partner(models.Model):
    _inherit = 'res.partner'
    
    code = fields.Many2one('product.delivery.code', ondelete='set null', string='Tarif DT')

