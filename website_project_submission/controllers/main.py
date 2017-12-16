# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request

from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.website.models.website import slug

class website_project_submission(http.Controller):
    @http.route([
        '/offers',
        '/offers/type/<model("project.offer.type"):type_id>',
        ], type='http', auth="public", website=True)
    
    def offers(self, type=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))

        offer_orm = env['project.offer']

        # List Offers available to current UID
        offer_ids = offer_orm.search([('state','=','open')], order="website_published desc, date_open desc").ids
        # Browse Offers as superuser, because address is restricted
        offers = offer_orm.sudo().browse(offer_ids)

        # Deduce types and offices of those Offers
        types = set(j.type for j in offers if j.type)

        # Filter the matching one
        if type:
            offers = (j for j in offers if j.type and j.type.id == type.id)

        # Render page
        return request.website.render("website_project_submission.index", {
            'offers': offers,
            'types': types,
            'type': type,
        })

    @http.route('/offers/add', type='http', auth="user", website=True)
    def offers_add(self, **kwargs):
        offer = request.env['project.offer'].create({
            'name': _('Nouvel Offre à projet'),
        })
        return request.redirect("/Offers/detail/%s?enable_editor=1" % slug(offer))

    @http.route('/offers/detail/<model("project.offer"):offer>', type='http', auth="public", website=True)
    def offers_detail(self, offer, **kwargs):
        return request.render("website_project_submission.detail", {
            'offer': offer,
            'main_object': offer,
        })

    @http.route('/offers/apply/<model("project.offer"):offer>', type='http', auth="public", website=True)
    def offers_apply(self, offer):
        if not request.session.uid:    
            return login_redirect()
        field_obj = http.request.env['project.offer.field']
        fields = field_obj.search([])
        error = {}
        default = {}
        if 'website_project_submission_error' in request.session:
            error = request.session.pop('website_project_submission_error')
            default = request.session.pop('website_project_submission_default')
        return request.render("website_project_submission.apply", {
            'offer': offer,
            'fields': fields,
            'error': error,
            'default': default,
        })

    def _get_submission_char_fields(self):
        return ['name', 'partner_mobile', 'description']

    def _get_submission_relational_fields(self):
        return ['field', 'offer', 'candidate']

    def _get_submission_files_fields(self):
        return ['ufile']

    def _get_submission_required_fields(self):
        return ['name', 'description', 'ufile', 'field']

    @http.route('/offers/thankyou', methods=['POST'], type='http', auth="public", website=True)
    def offers_thankyou(self, **post):
        if not request.session.uid:    
            return login_redirect()
        error = {}
        for field_name in self._get_submission_required_fields():
            if not post.get(field_name):
                error[field_name] = 'missing'
        if error:
            request.session['website_project_submission_error'] = error
            for field_name in self._get_submission_files_fields():
                f = field_name in post and post.pop(field_name)
                if f:
                    error[field_name] = 'reset'
            request.session['website_project_submission_default'] = post
            return request.redirect('/offers/apply/%s' % post.get("offer"))

        # public user can't create applicants (duh)
        env = request.env(user=SUPERUSER_ID)
        user = env['res.users'].browse(request.session.uid)
        candidate = env['project.candidate'].search([('user_id','=', user.id)])
        if candidate.id == False:
            candidate = env['project.candidate'].create({'user_id': user.id})
        value = {
            'name': post.get('name'), 
        }
        for f in self._get_submission_char_fields():
            value[f] = post.get(f)
        for f in self._get_submission_relational_fields():
            value[f] = int(post.get(f) or 0)
        # Retro-compatibility for saas-3. "phone" field should be replace by "partner_phone" in the template in trunk.
        value['candidate'] = candidate.id
        submission = env['project.submission'].create(value).id
        for field_name in self._get_submission_files_fields():
            if post[field_name]:
                attachment_value = {
                    'name': post[field_name].filename,
                    'res_name': value['name'],
                    'res_model': 'project.submission',
                    'res_id': submission,
                    'datas': base64.encodestring(post[field_name].read()),
                    'datas_fname': post[field_name].filename,
                }
                env['ir.attachment'].create(attachment_value)
        return request.render("website_project_submission.thankyou", {})

# vim :et:
