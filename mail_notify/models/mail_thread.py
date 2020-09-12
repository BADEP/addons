from odoo import  models
from pyfcm import FCMNotification
from html2text import html2text

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        res = super(MailThread, self)._notify_thread(message, msg_vals, **kwargs)
        if self.env['ir.config_parameter'].sudo().get_param('mail_notify.is_fcm_enabled'):
            push_service = FCMNotification(
                api_key=self.env['ir.config_parameter'].sudo().get_param('mail_notify.fcm_server_key'))
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
            message_values = message.message_format()[0]
            if self._name == 'mail.channel':
                icon = message.author_id and (
                            base_url + ('/web/image/res.partner/' + str(message.author_id.id) + '/image_small')) or (
                                   base_url + '/mail/static/src/img/smiley/avatar.jpg')
                web_tokens = (message.sudo().mapped(
                    'channel_ids.channel_partner_ids.user_ids') - message.sudo().author_id.user_ids).mapped(
                    'token_ids').filtered(lambda t: t.type == 'web').mapped('token')
                rel_url = '/web?#action=' + str(self.env.ref('mail.action_discuss').id) + '&active_id=' + str(self.id)
            else:
                if not message.model and self.env.context.get('default_res_id') and self.env.context.get(
                        'default_res_model'):
                    message.write({'model': self.env.context.get('default_res_model'),
                                   'res_id': self.env.context.get('default_res_id')})
                if not message.model and self.env.context.get('active_id') and self.env.context.get('active_model'):
                    message.write(
                        {'model': self.env.context.get('active_model'), 'res_id': self.env.context.get('active_id')})
                icon = message_values.get('module_icon') and message_values.get('module_icon') or \
                       message.author_id and '/web/image/res.partner/' + str(message.author_id.id) + '/image_small' or \
                       '/mail/static/src/img/smiley/avatar.jpg'
                web_tokens = message.sudo().notified_partner_ids.mapped('user_ids.token_ids').filtered(lambda t: t.type == 'web').mapped(
                    'token')
                rel_url = '/mail/view?message_id=' + str(message.id)
            if web_tokens:
                push_service.notify_multiple_devices(registration_ids=web_tokens,
                                                     message_title=message_values['author_id'][1],
                                                     message_icon=icon,
                                                     click_action=base_url + rel_url,
                                                     message_body=html2text(message_values['body']))
        return res
