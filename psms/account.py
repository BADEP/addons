# -*- coding: utf-8 -*-
from odoo import models, fields, api

class account_invoice(models.Model):
    _inherit = 'account.move'
    so_count = fields.Integer(compute='get_so_count', string='Nombre de bons')
    
    def get_so_count(self):
        self.so_count = self.env['sale.order'].search_count([('invoice_ids', 'in', self.id)])
