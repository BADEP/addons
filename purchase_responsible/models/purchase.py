# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    user_id = fields.Many2one('res.users', string='Responsable',
                                  readonly=True, states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.id)
    
    