from odoo import models
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses
import logging
_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for email in self:
            from_rfc2822 = extract_rfc2822_addresses(email.email_from)[-1]
            outgoing_mail_server = self.env['ir.mail_server'].search([('smtp_user', '=', from_rfc2822)], limit=1)
            if len(outgoing_mail_server):
                email.write({'mail_server_id': outgoing_mail_server.id})
            return super(MailMail, self).send(auto_commit=auto_commit, raise_exception=raise_exception)