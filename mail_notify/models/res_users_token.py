# -*- coding: utf-8 -*-

from odoo import api, fields, models
from pyfcm import FCMNotification


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

    @api.model
    def clean_token(self):
        push_service = FCMNotification(api_key=self.env['ir.config_parameter'].sudo().get_param('mail_notify.fcm_server_key'))
        tokens = self.sudo().search([()]).mapped('token')
        tokens = push_service.clean_registration_ids(tokens)
        self.sudo().search([('token', 'not in', tokens)]).unlink()