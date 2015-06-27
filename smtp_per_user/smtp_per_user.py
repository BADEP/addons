# -*- coding: utf-8 -*-

from openerp import models, fields, api, SUPERUSER_ID, tools
from openerp.osv import osv
import threading

class ir_mail_server(models.Model):
    _inherit = "ir.mail_server"

    user_id = fields.Many2one('res.users', string="Owner")

    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False):
        mail_server = self.search([('user_id', '=', self.env.uid)], limit=1)
        if mail_server:
            mail_server_id = mail_server.id
        return super(ir_mail_server, self).send_email(message, mail_server_id, smtp_server, smtp_port,
                   smtp_user, smtp_password, smtp_encryption, smtp_debug)

ir_mail_server()

class mail_notification(osv.Model):
    _inherit = "mail.notification"
    
    def _notify(self, cr, uid, message_id, partners_to_notify=None, context=None,
                force_send=False, user_signature=True):
        """ Send by email the notification depending on the user preferences

            :param list partners_to_notify: optional list of partner ids restricting
                the notifications to process
            :param bool force_send: if True, the generated mail.mail is
                immediately sent after being created, as if the scheduler
                was executed for this message only.
            :param bool user_signature: if True, the generated mail.mail body is
                the body of the related mail.message with the author's signature
        """
        notif_ids = self.search(cr, SUPERUSER_ID, [('message_id', '=', message_id), ('partner_id', 'in', partners_to_notify)], context=context)

        # update or create notifications
        new_notif_ids = self.update_message_notification(cr, SUPERUSER_ID, notif_ids, message_id, partners_to_notify, context=context)

        # mail_notify_noemail (do not send email) or no partner_ids: do not send, return
        if context and context.get('mail_notify_noemail'):
            return True

        # browse as SUPERUSER_ID because of access to res_partner not necessarily allowed
        self._notify_email(cr, uid, new_notif_ids, message_id, force_send, user_signature, context=context)


    def _notify_email(self, cr, uid, ids, message_id, force_send=False, user_signature=True, context=None):
        message = self.pool['mail.message'].browse(cr, SUPERUSER_ID, message_id, context=context)

        # compute partners
        email_pids = self.get_partners_to_email(cr, SUPERUSER_ID, ids, message, context=None)
        if not email_pids:
            return True

        # compute email body (signature, company data)
        body_html = message.body
        # add user signature except for mail groups, where users are usually adding their own signatures already
        user_id = message.author_id and message.author_id.user_ids and message.author_id.user_ids[0] and message.author_id.user_ids[0].id or None
        signature_company = self.get_signature_footer(cr, SUPERUSER_ID, user_id, res_model=message.model, res_id=message.res_id, context=context, user_signature=(user_signature and message.model != 'mail.group'))
        if signature_company:
            body_html = tools.append_content_to_html(body_html, signature_company, plaintext=False, container_tag='div')

        # compute email references
        references = message.parent_id.message_id if message.parent_id else False

        # custom values
        custom_values = dict()
        if message.model and message.res_id and self.pool.get(message.model) and hasattr(self.pool[message.model], 'message_get_email_values'):
            custom_values = self.pool[message.model].message_get_email_values(cr, uid, message.res_id, message, context=context)

        # create email values
        max_recipients = 50
        chunks = [email_pids[x:x + max_recipients] for x in xrange(0, len(email_pids), max_recipients)]
        email_ids = []
        for chunk in chunks:
            mail_values = {
                'mail_message_id': message.id,
                'auto_delete': True,
                'body_html': body_html,
                'recipient_ids': [(4, id) for id in chunk],
                'references': references,
            }
            mail_values.update(custom_values)
            email_ids.append(self.pool.get('mail.mail').create(cr, SUPERUSER_ID, mail_values, context=context))
        # NOTE:
        #   1. for more than 50 followers, use the queue system
        #   2. do not send emails immediately if the registry is not loaded,
        #      to prevent sending email during a simple update of the database
        #      using the command-line.
        if force_send and len(chunks) < 2 and \
               (not self.pool._init or
                getattr(threading.currentThread(), 'testing', False)):
            self.pool.get('mail.mail').send(cr, uid, email_ids, context=context)
        return True