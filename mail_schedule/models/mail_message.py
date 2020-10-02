from odoo import  models, api, fields

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    scheduled_date = fields.Datetime('Scheduled date')

    @api.multi
    def get_mail_values(self, res_ids):
        res = super().get_mail_values(res_ids)
        for id in res_ids:
            res[id].update({'scheduled_date': self.scheduled_date})
        return res

class MailMessage(models.Model):
    _inherit = 'mail.message'

    def _notify_recipients(self, rdata, record, msg_vals,
                           force_send=False, send_after_commit=True,
                           model_description=False, mail_auto_delete=True):
        return super(MailMessage, self.with_context(scheduled_date = msg_vals.get('scheduled_date')))._notify_recipients(rdata, record, msg_vals,
                           force_send=False if msg_vals.get('scheduled_date') else force_send, send_after_commit=send_after_commit,
                           model_description=model_description, mail_auto_delete=mail_auto_delete)

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, values):
        if self.env.context.get('scheduled_date'):
            values.update({'scheduled_date': self.env.context.get('scheduled_date')})
        return super().create(values)