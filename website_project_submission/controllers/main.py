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
        '/offers/type/<model("project.offer.type"):type>',
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
                 '/offers/apply/<model("project.offer"):offer>/stage/<int:next_stage>'
                 ], type='http', auth="public", website=True)
    def offers_apply(self, offer=None, next_stage=None, **post):
        
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
        if not submission:
            submission = env['project.submission'].create({
                                                           'name': '/',
                                                           'offer': offer.id,
                                                           'candidate': candidate.id,})
        
        #Save the current stage
        current_stage = post.get('current_stage') and int(post.get('current_stage'))
        if bool(post):
            if post.get('unlink-doc'):
                env['ir.attachment'].browse(int(post.get('unlink-doc'))).unlink()
            if post.get('unlink-partner'):
                submission.write({'partners': [(3, int(post.get('unlink-partner')))]})
                partner = env['res.partner'].browse(int(post.get('unlink-partner')))
                if not partner.submissions:
                    partner.unlink()
            #Stage 0: Project general informations
            if current_stage == 0:
                value = {
                    'name': post.get('name'),
                    'acronyme': post.get('acronyme'),
                    'duration': post.get('duration'),
                    'field': [(6, 0, [int(x) for x in request.httprequest.form.getlist('fields')])],
                    'description': post.get('description'),
                }
                submission.write(value)
                if post.get('ufile'):
                    submission.documents.unlink()
                    attachment_value = {
                        'name': post['ufile'].filename,
                        'res_name': value['name'],
                        'res_model': 'project.submission',
                        'res_id': submission.id,
                        'datas': base64.encodestring(post['ufile'].read()),
                        'datas_fname': post['ufile'].filename,
                    }
                    env['ir.attachment'].create(attachment_value)
                    submission._get_attached_docs()

            #Stage 1: Candidate general informations
            elif current_stage == 1:
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
                if post.get('ufile'):
                    attachment_value = {
                        'name': post['ufile'].filename,
                        'res_name': value['name'],
                        'res_model': 'project.candidate',
                        'res_id': candidate.id,
                        'datas': base64.encodestring(post['ufile'].read()),
                        'datas_fname': post['ufile'].filename,
                    }
                    env['ir.attachment'].create(attachment_value)
                    candidate._get_attached_docs()

            #Stage 2: Project partners informations
            elif current_stage == 2 and post.get('to-save') == "1":
                partner_organisme = env['res.partner'].create({'name': post.get('organisme')})
                partner_value = {
                    'name': post.get('name'),
                    'function': post.get('function'),
                    'phone': post.get('phone'),
                    'mobile': post.get('mobile'),
                    'image': post.get('image'),
                    'fax': post.get('fax'),
                    'email': post.get('email'),
                    'parent_id': partner_organisme.id,
                    'category': post.get('category'),
                    'submissions': [(4, submission.id)]
                }
                if post.get('partner_id') != 'None':
                    partner = env['res.partner'].browse(int(post.get('partner_id')))
                    partner.write(partner_value)
                else:
                    partner = env['res.partner'].create(partner_value)
            #Stage 3: Project budget informations
            elif current_stage == 3:
                value = {
                    'type': post.get('type'),
                    'budget': post.get('budget'),
                    'montant_propre': float(post.get('budget')) - float(post.get('montant_propre')),
                    'submission': submission.id,
                }
                env['project.submission.budgetline'].create(value)
                if post.get('submit') == 'add':
                    return request.redirect("/offers/apply/%s/stage/3" % slug(offer))     
            elif current_stage == 4:
                dummy=0
        
        if next_stage == None:
            if bool(post) and post.get('submit') == 'next':
                next_stage = current_stage + 1
            elif bool(post) and post.get('submit') == 'prev':
                next_stage = current_stage - 1
            elif bool(post) and current_stage:
                next_stage = current_stage
            else:
                next_stage = 0
                
        #prepare next_stage vals
        vals = {
                'offer': offer,
                'submission': submission,
                'candidate': candidate,
                'error': error,
                'default': default,
                'current_stage': next_stage,
                }
        if next_stage == 0:
            fields = env['project.offer.field'].search([])
            if submission:
                default['name'] = submission.name
                default['acronyme'] = submission.acronyme
                default['field'] = submission.field.ids
                default['duration'] = submission.duration
                default['description'] = submission.description
            duration_steps = range(offer.min_time, offer.max_time + 1)
            vals.update({
                'error': error,
                'default': default,
                'duration_steps': duration_steps,
                'fields': fields,
            })
        if next_stage == 1:
            default['name'] = candidate.name
            default['organisme'] = candidate.parent_id and candidate.parent_id.name
            default['function'] = candidate.function
            default['phone'] = candidate.phone
            default['mobile'] = candidate.mobile
            default['email'] = candidate.email if candidate.email else candidate.login

            vals.update({
                'error': error,
                'default': default,
            })
        elif next_stage == 2:
            categories = [('scientifique', 'Scientifique'), ('industriel', 'Industriel')]
            duration_steps = range(1, offer.max_time + 1)
            if post.get('edit-partner'):
                partner = env['res.partner'].browse(int(post.get('edit-partner')))
                vals.update({'partner_id': partner.id})
                default.update({
                    'category': partner.category,
                    'image': partner.image,
                    'name': partner.name,
                    'organisme': partner.parent_id.name,
                    'function': partner.function,
                    'phone': partner.phone,
                    'mobile': partner.mobile,
                    'fax': partner.fax,
                    'email': partner.email,
                })
            vals.update({
                'duration_steps': duration_steps,
                'categories': categories,
                'error': error,
                'default': default,
            })
        elif next_stage == 3:
            types = env['project.budgetline.type'].search([])
            vals.update({
                'types': types,
                'error': error,
                'default': default,
            })
        elif next_stage == 4:
            types = env['project.submission.task.type'].search([])
            vals.update({
                'types': types,
                'error': error,
                'default': default,
            })
            """if submission.survey:  
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
            })"""
        return request.render('website_project_submission.apply', vals)
# vim :et:
