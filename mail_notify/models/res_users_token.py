# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsersToken(models.Model):
    _name = 'res.users.token'

    user_id = fields.Many2one('res.users', ondelete='cascade')
    token = fields.Char(required=True)

    _sql_constraints = [
        ('token_uniq', 'unique(token)', 'Token must be unique!'),
    ]

    @api.model
    def add_token(self, token):
        if self.sudo().search([('token', '=', token)]):
            self.sudo().search([('token', '=', token)]).write({'user_id': self.env.user.id})
        else:
            self.sudo().create({'token': token, 'user_id': self.env.user.id})
