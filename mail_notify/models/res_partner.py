# -*- coding: utf-8 -*-
from odoo import fields, models, api
from pyfcm import FCMNotification
from html2text import html2text


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _notify_by_chat(self, message):
        res = super(ResPartner, self)._notify_by_chat(message)
        for partner in self.sudo():
            tokens = partner.mapped('user_ids.token_ids.token')
            if tokens:
                push_service = FCMNotification(api_key=self.env['ir.config_parameter'].sudo().get_param('mail_notify.fcm_server_key'))
                message_values = message.message_format()[0]
                result = push_service.notify_multiple_devices(registration_ids = tokens,
                                                              message_title=message_values['author_id'][1] + ': ' + (message_values['subject'] or message_values['record_name']),
                                                              message_icon= message_values['module_icon'],
                                                              click_action = '/mail/view?message_id=' + str(message.id),
                                                              message_body=html2text(message_values['body']))
        return res