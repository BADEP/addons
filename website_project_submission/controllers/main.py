# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request

from openerp.addons.website.models.website import slug

class website_project_submission(http.Controller):
    @http.route([
        '/Offers',
        '/Offers/type/<model("project.offer.type"):type>',
    ], type='http', auth="public", website=True)
    def Offers(self, type=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))

        Country = env['res.country']
        offers = env['project.offer']

        # List Offers available to current UID
        offers = offers.search([], order="website_published desc,no_of_recruitment desc").ids
        # Browse Offers as superuser, because address is restricted
        offers = offers.sudo().browse(offers)

        # Deduce types and offices of those Offers
        types = set(j.type_id for j in offers if j.type_id)
        offices = set(j.address_id for j in offers if j.address_id)
        countries = set(o.country_id for o in offices if o.country_id)

        # Default search by user country
        if not (country or type or office_id or kwargs.get('all_countries')):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                countries_ = Country.search([('code', '=', country_code)])
                country = countries_[0] if countries_ else None
                if not any(j for j in offers if j.address_id and j.address_id.country_id == country):
                    country = False

        # Filter the matching one
        if country and not kwargs.get('all_countries'):
            Offers = (j for j in Offers if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id)
        if type:
            Offers = (j for j in Offers if j.type_id and j.type_id.id == type.id)
        if office_id:
            Offers = (j for j in Offers if j.address_id and j.address_id.id == office_id)

        # Render page
        return request.website.render("website_project_submission.index", {
            'Offers': Offers,
            'countries': countries,
            'types': types,
            'offices': offices,
            'country_id': country,
            'type_id': type,
            'office_id': office_id,
        })

    @http.route('/Offers/add', type='http', auth="user", website=True)
    def Offers_add(self, **kwargs):
        job = request.env['project.offer'].create({
            'name': _('Nouveau Offre de projet'),
        })
        return request.redirect("/Offers/detail/%s?enable_editor=1" % slug(job))

    @http.route('/Offers/detail/<model("project.offer"):offer>', type='http', auth="public", website=True)
    def Offers_detail(self, offer, **kwargs):
        return request.render("website_hr_recruitment.detail", {
            'offer': offer,
            'main_object': offer,
        })

    @http.route('/Offers/apply/<model("project.offer"):offer>', type='http', auth="public", website=True)
    def Offers_apply(self, offer):
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_project_submission_error')
            default = request.session.pop('website_project_submission_default')
        return request.render("website_project_submission.apply", {
            'offer': offer,
            'error': error,
            'default': default,
        })

    def _get_applicant_char_fields(self):
        return ['email_from', 'partner_name', 'description']

    def _get_applicant_relational_fields(self):
        return ['type_id', 'offer']

    def _get_applicant_files_fields(self):
        return ['ufile']

    def _get_candidate_required_fields(self):
        return ["partner_name", "phone", "email_from"]

    @http.route('/Offers/thankyou', methods=['POST'], type='http', auth="public", website=True)
    def Offers_thankyou(self, **post):
        error = {}
        for field_name in self._get_candidate_required_fields():
            if not post.get(field_name):
                error[field_name] = 'missing'
        if error:
            request.session['website_project_submission_error'] = error
            for field_name in self._get_candidate_files_fields():
                f = field_name in post and post.pop(field_name)
                if f:
                    error[field_name] = 'reset'
            request.session['website_project_submission_default'] = post
            return request.redirect('/Offers/apply/%s' % post.get("offer"))

        # public user can't create applicants (duh)
        env = request.env(user=SUPERUSER_ID)
        value = {
            'source_id' : env.ref('project_submission.source_website_company').id,
            'name': '%s\'s Application' % post.get('partner_name'), 
        }
        for f in self._get_candidate_char_fields():
            value[f] = post.get(f)
        for f in self._get_candidate_relational_fields():
            value[f] = int(post.get(f) or 0)
        # Retro-compatibility for saas-3. "phone" field should be replace by "partner_phone" in the template in trunk.
        value['partner_phone'] = post.pop('phone', False)

        candidate = env['project.candidate'].create(value).id
        for field_name in self._get_candidate_files_fields():
            if post[field_name]:
                attachment_value = {
                    'name': post[field_name].filename,
                    'res_name': value['partner_name'],
                    'res_model': 'project.candidate',
                    'res_id': candidate,
                    'datas': base64.encodestring(post[field_name].read()),
                    'datas_fname': post[field_name].filename,
                }
                env['ir.attachment'].create(attachment_value)
        return request.render("website_hr_recruitment.thankyou", {})

# vim :et:
