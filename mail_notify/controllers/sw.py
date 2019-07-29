from odoo import http, _
from odoo.tools.translate import _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from werkzeug.exceptions import NotFound
from odoo.http import root

class ServiceWorker(http.Controller):


    @http.route('/firebase-messaging-sw.js', type='http', auth="public", website=True)
    def get_sw(self, **kwargs):
        message_id = request.env['ir.config_parameter'].get_fcm_config()['fcm_messaging_id'] or '1234567890'
        code = """
importScripts('https://www.gstatic.com/firebasejs/6.3.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/6.3.1/firebase-messaging.js');
var firebaseConfig = {
    messagingSenderId: '%s'
};
firebase.initializeApp(firebaseConfig);

var messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
  console.log('Handling background message ', payload);

  return self.registration.showNotification(payload.data.title, {
    body: payload.data.body,
    icon: payload.data.icon,
    tag: payload.data.tag,
    data: payload.data.link
  });
});
""" % message_id
        return request.make_response(code, [('Content-Type', 'text/javascript')])

    @http.route('/register_mobile/<string:session_id>/<string:token>', type='http', auth="public", website=True)
    def register_mobile(self, session_id, token, **kwargs):
        session = root.session_store.get(session_id)
