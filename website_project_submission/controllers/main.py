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
        return request.redirect("/offers/detail/%s?enable_editor=1" % slug(offer))

    @http.route('/offers/detail/<model("project.offer"):offer>', type='http', auth="public", website=True)
    def offers_detail(self, offer, **kwargs):
        return request.render("website_project_submission.detail", {
            'offer': offer,
            'main_object': offer,
        })

    @http.route(['/offers/apply/<model("project.offer"):offer>',
                 '/offers/apply/<model("project.offer"):offer>/stage/<int:stage>'
                 ], type='http', auth="public", website=True)
    def offers_apply(self, offer=None, stage=None, **post):
        
        #If no user connected, force connection
        #TODO: Redirect to submission page if offer variable is in session
        if not request.session.uid:
            request.session['offer'] = offer.id
            return login_redirect()
        
        #Get error data
        error = {}
        default = {}
        if 'website_project_submission_error' in request.session:
            error = request.session.pop('website_project_submission_error')
            default = request.session.pop('website_project_submission_default')
            
        #Get the candidate, if no candidate create one
        env = request.env(user=SUPERUSER_ID)
        user = env['res.users'].browse(request.session.uid)
        candidate = env['project.candidate'].search([('user','=', user.id)])
        if candidate.id == False:
            candidate = env['project.candidate'].create({'user': user.id})

        #Get the submission, if no submission call creation template
        submission = env['project.submission'].search([('offer', '=', offer.id), ('candidate', '=', candidate.id)])
        stage = 0 if (submission.id == False and bool(post) == False) else min(stage, submission.get_early_stage()) if stage != None else submission.get_early_stage()[0]
        if stage == 0:
            fields = env['project.offer.field'].search([])
            ## SET SWITCH TO TEMPLATES ACCORDING TO SUBMISSION STATE
            if submission:
                default['name'] = submission.name
                default['acronyme'] = submission.acronyme
                default['field'] = submission.field.id
                default['duration'] = submission.duration
                default['description'] = submission.description
            duration_steps = range(offer.min_time, offer.max_time + 1)
            return request.render("website_project_submission.apply0", {
                'offer': offer,
                'duration_steps': duration_steps,
                'fields': fields,
                'error': error,
                'default': default,
            })
        if stage == 1:
            default['name'] = candidate.name
            default['organisme'] = candidate.parent_id and candidate.parent_id.name
            default['function'] = candidate.function
            default['phone'] = candidate.phone
            default['mobile'] = candidate.mobile
            default['email'] = candidate.email if candidate.email else candidate.login
            
            if bool(post):
                value = {
                    'name': post.get('name'),
                    'acronyme': post.get('acronyme'),
                    'offer': offer.id,
                    'candidate': candidate.id,
                    'field': int(post.get('field')),
                    'description': post.get('description'),
                }
                if submission:
                    submission.write(value)
                else:
                    submission = env['project.submission'].create(value)
                attachment_value = {
                    'name': post['ufile'].filename,
                    'res_name': value['name'],
                    'res_model': 'project.submission',
                    'res_id': submission.id,
                    'datas': base64.encodestring(post['ufile'].read()),
                    'datas_fname': post['ufile'].filename,
                }
                env['ir.attachment'].create(attachment_value)
            return request.render("website_project_submission.apply1", {
                'offer': offer,
                'submission': submission,
                'candidate': candidate,
                'error': error,
                'default': default,
            })
        elif stage == 2:
            if bool(post):
                value = {
                    'name': post.get('name'),
                    'function': post.get('function'),
                    'phone': post.get('phone'),
                    'mobile': post.get('mobile'),
                    'email': post.get('email'),
                }
                candidate.write(value)
                if candidate.parent_id:
                    candidate.parent_id.write({'name': post.get('organisme')})
                else:
                    organisme = env['res.partner'].create({'name': post.get('organisme')})
                    candidate.write({'parent_id': organisme.id})
                attachment_value = {
                    'name': post['ufile'].filename,
                    'res_name': value['name'],
                    'res_model': 'project.candidate',
                    'res_id': candidate.id,
                    'datas': base64.encodestring(post['ufile'].read()),
                    'datas_fname': post['ufile'].filename,
                }
                env['ir.attachment'].create(attachment_value)
            types = env['project.partner.type'].search([])
            duration_steps = range(1, offer.max_time + 1)
            return request.render("website_project_submission.apply2", {
                'offer': offer,
                'types': types,
                'duration_steps': duration_steps,
                'submission': submission,
                'partners': submission.partners,
                'error': error,
                'default': default,
            })
        elif stage == 3:
            if bool(post):
                partner_organisme = env['res.partner'].create({'name': post.get('organisme')})
                partner_value = {
                    'name': post.get('name'),
                    'function': post.get('function'),
                    'phone': post.get('phone'),
                    'mobile': post.get('mobile'),
                    'email': post.get('email'),
                    'parent_id': partner_organisme.id,
                }
                partner = env['res.partner'].create(partner_value)
                submission_value = {
                    'type': post.get('type'),
                    'function': post.get('function'),
                    'montant': post.get('montant'),
                    'time': post.get('time'),
                    'submission': submission.id,
                    'partner': partner.id,
                }
                submission_partner = env['project.submission.partner'].create(submission_value)
                if post.get('submit') == 'add':
                    return request.redirect("/offers/apply/%s/stage/2" % slug(offer))
            types = env['project.budgetline.type'].search([])
            return request.render("website_project_submission.apply3", {
                'offer': offer,
                'types': types,
                'submission': submission,
                'error': error,
                'default': default,
            })
        elif stage == 4:
            if bool(post):
                value = {
                    'type': post.get('type'),
                    'budget': post.get('budget'),
                    'montant_propre': float(post.get('budget')) - float(post.get('montant_propre')),
                    'submission': submission.id,
                }
                budget_line = env['project.submission.budgetline'].create(value)
                if post.get('submit') == 'add':
                    return request.redirect("/offers/apply/%s/stage/3" % slug(offer))
            if submission.survey:  
                if not submission.response:
                    response = env['survey.user_input'].create({'survey_id': submission.survey.id, 'partner_id': candidate.user.partner_id.id})
                    submission.write({'response': response.id})
                else:
                    response = submission.response
                return request.redirect("/survey/fill/%s/%s" % (slug(submission.survey), response.token))
            return request.render("website_project_submission.thankyou", {
                'offer': offer,
                'submission': submission,
                'error': error,
                'default': default,
            })

# vim :et:
