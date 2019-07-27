# -*- coding: utf-8 -*-
from odoo import fields, models, api
from pyfcm import FCMNotification
from html2text import html2text


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    @api.multi
    def _notify(self, message):
        res = super(MailChannel, self)._notify(message)
        tokens = (message.sudo().mapped('channel_ids.channel_partner_ids.user_ids') - message.sudo().author_id.user_ids).mapped('token_ids.token')
        if tokens:
            push_service = FCMNotification(api_key=self.env['ir.config_parameter'].sudo().get_param('mail_notify.fcm_server_key'))
            message_values = message.message_format()[0]
            icon = message.author_id and ('/web/image/res.partner/' + str(message.author_id.id) + '/image_small') or '/mail/static/src/img/smiley/avatar.jpg'
            result = push_service.notify_multiple_devices(registration_ids = tokens,
                                                          message_title=message_values['author_id'][1],
                                                          message_icon= icon,
                                                          click_action = '/mail/view?message_id=' + str(message.id),
                                                          message_body=html2text(message_values['body']))
        return res