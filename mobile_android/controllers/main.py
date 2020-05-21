from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import Home

class FirebaseHome(Home):
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        response = super(FirebaseHome, self).web_client(s_action, **kw)
        token = request.httprequest.cookies.get('token', False)
        if token and request.env.user.id:
            request.env['res.users.token'].add_token(token, request.httprequest.cookies.get('token_type', False))
            response.set_cookie('token', expires=0)
        return response