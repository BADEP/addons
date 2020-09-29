from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_fcm_enabled = fields.Boolean('Use FCM for Push Notifications', config_parameter='mail_notify.is_fcm_enabled')
    fcm_server_key = fields.Char('Server API Key', config_parameter='mail_notify.fcm_server_key')
    fcm_vapid_key = fields.Char('VAPID Key', config_parameter='mail_notify.fcm_vapid_key')
    fcm_messaging_id = fields.Char('Messaging ID', config_parameter='mail_notify.fcm_messaging_id')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            is_fcm_enabled=get_param('mail_notify.is_fcm_enabled', default=False),
            fcm_server_key=get_param('mail_notify.fcm_server_key', ''),
            fcm_vapid_key=get_param('mail_notify.fcm_vapid_key', ''),
            fcm_messaging_id=get_param('mail_notify.fcm_messaging_id', '')
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('mail_notify.is_fcm_enabled', self.is_fcm_enabled)
        set_param('mail_notify.fcm_server_key', self.fcm_server_key)
        set_param('mail_notify.fcm_vapid_key', self.fcm_vapid_key)
        set_param('mail_notify.fcm_messaging_id', self.fcm_messaging_id)
#     badge = fields.Binary('Badge', related='company_id.badge', readonly=False)
#
# class ResCompany(models.Model):
#     _inherit = 'res.company'
#
#     badge = fields.Binary('Badge')