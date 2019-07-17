# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.tools import pycompat


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _message_post_get_pid(self):
        self.ensure_one()
        if 'thread_model' in self.env.context:
            self = self.with_context(thread_model='res.users')
        return self.partner_id.id

    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, **kwargs):
        """ Redirect the posting of message on res.users as a private discussion.
            This is done because when giving the context of Chatter on the
            various mailboxes, we do not have access to the current partner_id. """
        current_pids = []
        partner_ids = kwargs.get('partner_ids', [])
        user_pid = self._message_post_get_pid()
        for partner_id in partner_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                current_pids.append(partner_id[1])
            elif isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                current_pids.append(partner_id[2])
            elif isinstance(partner_id, pycompat.integer_types):
                current_pids.append(partner_id)
        if user_pid not in current_pids:
            partner_ids.append(user_pid)
        kwargs['partner_ids'] = partner_ids
        return self.env['mail.thread'].message_post(**kwargs)

    def message_update(self, msg_dict, update_vals=None):
        return True

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
        return True

    @api.multi
    def message_partner_info_from_emails(self, emails, link_mail=False):
        return self.env['mail.thread'].message_partner_info_from_emails(emails, link_mail=link_mail)

    @api.multi
    def message_get_suggested_recipients(self):
        return dict((res_id, list()) for res_id in self._ids)

    @api.multi
    def action_create_alias(self):
        for rec in self:
            alias_id = self.env['mail.alias'].create({
                'alias_name': rec.login.split('@')[0],
                'alias_model_id': self.env.ref('base.model_res_users').id,
                'alias_force_thread_id': rec.id,
                'alias_parent_model_id': self.env.ref('base.model_res_users').id,
                'alias_defaults': "{'user_id':" + str(rec.id) + "}",
                'alias_contact': 'everyone',
                'alias_parent_thread_id': rec.id
            })
            rec.write({
                'alias_id': alias_id.id,
                'notification_type': 'inbox'
            })
