from odoo.models import api, Model
from odoo.tools.safe_eval import const_eval


class IrConfigParameter(Model):
    _inherit = "ir.config_parameter"

    @api.model
    def get_crm_facebook_config(self):
        get_param = self.sudo().get_param
        return {
            'crm_fb_app_id': const_eval(get_param("crm_facebook_leads.crm_fb_app_id", 'False')),
            'crm_fb_app_secret': get_param("crm_facebook_leads.crm_fb_app_secret", 'False'),
            'crm_fb_access_token': get_param("crm_facebook_leads.crm_fb_access_token", 'False'),
        }
