from odoo import models, api, fields


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    scheduled_date = fields.Datetime('Scheduled date')

    def get_mail_values(self, res_ids):
        res = super().get_mail_values(res_ids)
        for id in res_ids:
            res[id].update({'scheduled_date': self.scheduled_date})
        return res


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_record_by_email(self, message, recipients_data, msg_vals=False,
                                model_description=False, mail_auto_delete=True, check_existing=False,
                                force_send=True, send_after_commit=True,
                                **kwargs):
        return super(MailThread, self.with_context(scheduled_date=kwargs.get('scheduled_date')))._notify_record_by_email(message=message,
                                                                                                                         recipients_data=recipients_data,
                                                                                                                         msg_vals=msg_vals,
                                                                                                                         model_description=model_description,
                                                                                                                         mail_auto_delete=mail_auto_delete,
                                                                                                                         check_existing=check_existing,
                                                                                                                         force_send=False if kwargs.get(
                                                                                                                           'scheduled_date') else force_send,
                                                                                                                         send_after_commit=send_after_commit,
                                                                                                                         **kwargs)

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, values):
        if self.env.context.get('scheduled_date'):
            values.update({'scheduled_date': self.env.context.get('scheduled_date')})
        return super().create(values)
