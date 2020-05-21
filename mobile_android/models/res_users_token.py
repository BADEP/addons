from odoo import api, fields, models
from pyfcm import FCMNotification

class ResUsersToken(models.Model):
    _inherit = 'res.users.token'

    type = fields.Selection(selection_add=[('android', 'Android')], default='web', required=True)