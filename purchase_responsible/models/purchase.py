# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    user_id = fields.Many2one('res.users', string='Responsable',
                                  readonly=True, states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.id)
    
    