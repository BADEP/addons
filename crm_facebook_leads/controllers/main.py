import functools
import logging
import requests, werkzeug
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


def fragment_to_query_string(func):
    @functools.wraps(func)
    def wrapper(self, *a, **kw):
        kw.pop('debug', False)
        if not kw:
            return """<html><head><script>
                var l = window.location;
                var q = l.hash.substring(1);
                var r = l.pathname + l.search;
                if(q.length !== 0) {
                    var s = l.search ? (l.search === '?' ? '' : '&') : '?';
                    r = l.pathname + l.search + s + q;
                }
                if (r == l.pathname) {
                    r = '/';
                }
                window.location = r;
            </script></head><body></body></html>"""
        return func(self, *a, **kw)

    return wrapper


class OAuthController(http.Controller):

    @http.route('/crm_facebook_leads/auth', type='http', auth='user', website='False')
    @fragment_to_query_string
    def add_access_token(self, **kw):
        if kw.get('access_token'):
            params = {
                'client_id': request.env['ir.config_parameter'].sudo().get_param('crm_facebook_leads.crm_fb_app_id'),
                'client_secret': request.env['ir.config_parameter'].sudo().get_param(
                    'crm_facebook_leads.crm_fb_app_secret'),
                'fb_exchange_token': kw.get('access_token')
            }
            r = requests.get("https://graph.facebook.com/v7.0/oauth/access_token?grant_type=fb_exchange_token",
                             params=params).json()
            if r.get('error'):
                _logger.log(r.get('error').get('message'))
            request.env['ir.config_parameter'].set_param("crm_facebook_leads.crm_fb_access_token",
                                                         r.get('access_token', ''))
        config_action = request.env.ref('crm.crm_config_settings_action')
        url = "/web#view_type=form&model=res.config.settings&action={}".format(
            config_action and config_action.id or ''
        )
        return werkzeug.utils.redirect(url)
