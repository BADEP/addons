# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.tools import decode_message_header
import email
from xmlrpc import client

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):
        if isinstance(message, client.Binary):
            message = str(message.data)
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        msg_txt = email.message_from_string(message)
        email_to = decode_message_header(msg_txt, 'To')
        if '.amazonses.com' in msg_txt['Message-Id']:
            new_message_id = self.env['mail.mail'].browse(int(email_to.split('@')[0].split('+')[1].split('-')[0])).message_id
            msg_txt.replace_header('Message-Id', new_message_id)
        msg = self.message_parse(msg_txt, save_original=save_original)

        routes = self.message_route(msg_txt, msg, model, thread_id, custom_values)
        if 'bounce' in msg_txt['To']:
            message_id = self.env['mail.message'].search([('message_id', '=', msg_txt['Message-Id'])])
            if message_id:
                tracking_id = self.env['mail.tracking.email'].search([('mail_message_id', '=', message_id.id)])
                tracking_id.write({'state': 'bounced'})
                tracking_id.event_create('hard_bounce', {'bounce_type': 'hard_bounce', 'bounce_description': 'Bounced'})
        thread_id = self.message_route_process(msg_txt, msg, routes)
        return thread_id
