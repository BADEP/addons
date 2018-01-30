# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request

from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.website.models.website import slug
from openerp.exceptions import ValidationError
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.addons.web.controllers.main import ensure_db

class WebInherit(AuthSignupHome):
    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(WebInherit, self).web_login(*args, **kw)
        if request.session.get('offer'):
            response.qcontext.update({'redirect': '/offers/apply/' + str(request.session['offer'])})
        else:
            response.qcontext.update({'redirect': '/my/home/'})
        return response

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
            request.session.update({'offer': offer.id})
            return login_redirect()
        
        #Get error data
        error = {}
        if 'website_project_submission_error' in request.session:
            error = request.session.pop('website_project_submission_error')
            
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
        
        has_exception = False
        #Save the current stage
        current_stage = post.get('current_stage') and int(post.get('current_stage'))
        try:
            if bool(post) and post.get('submit') != 'cancel':
                if post.get('unlink-doc'):
                    env['ir.attachment'].browse(int(post.get('unlink-doc'))).unlink()
                if post.get('unlink-task'):
                    env['project.submission.task'].browse(int(post.get('unlink-task'))).unlink()
                if post.get('unlink-partner'):
                    submission.write({'partners': [(3, int(post.get('unlink-partner')))]})
                    partner = env['res.partner'].browse(int(post.get('unlink-partner')))
                    if not partner.submissions:
                        partner.unlink()
                if post.get('unlink-budgetline'):
                    env['project.submission.budgetline'].browse(int(post.get('unlink-budgetline'))).unlink()
                #Stage 1: Project general informations
                if current_stage == 1:
                    value = {
                        'name': post.get('name'),
                        'acronyme': post.get('acronyme'),
                        'duration': post.get('duration'),
                        'field_ids': [(6, 0, [int(x) for x in request.httprequest.form.getlist('fields')])],
                        'keywords': post.get('keywords'),
                        'description': post.get('description'),
                        'n_related_publications': post.get('n_related_publications'),
                        'n_ing_doc': post.get('n_ing_doc'),
                        'n_master_pfe': post.get('n_master_pfe'),
                    }
                    submission.write(value)
                #Stage 2: Candidate general informations
                elif current_stage == 2:
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
    
                #Stage 3: Project partners informations
                elif (current_stage == 3 or current_stage == 4) and post.get('to-save') == "1" and post.get('name'):
                    #partner_organisme = env['res.partner'].create({'name': post.get('organisme')})
                    partner_value = {
                        'name': post.get('name'),
                        'country': post.get('country'),
                        'city': post.get('city'),
                        'zip': post.get('zip'),
                        'street': post.get('street'),
                        'email': post.get('email'),
                        'phone': post.get('phone'),
                        'fax': post.get('fax'),
                        'email': post.get('email'),
                        'website': post.get('website'),
                        #'parent_id': partner_organisme.id,
                        'category': 'scientifique' if current_stage == 3 else 'industriel',
                        'submissions': [(4, submission.id)]
                    }
                    if post.get('partner_id') is not None:
                        partner = env['res.partner'].browse(int(post.get('partner_id')))
                        partner.write(partner_value)
                    else:
                        partner = env['res.partner'].create(partner_value)
                    contact_value = {
                        'name': post.get('contact_name'),
                        'function': post.get('contact_function'),
                        'phone': post.get('contact_phone'),
                        'email': post.get('contact_email'),
                        'parent_id': partner.id,
                        'category': 'scientifique' if current_stage == 3 else 'industriel',
                        'submissions': [(4, submission.id)]
                    }
                    contact = partner.child_ids.filtered(lambda c: c.name == post.get('contact_name'))
                    if contact:
                        contact[0].write(contact_value)
                    else:
                        contact = env['res.partner'].create(contact_value)
                    if post.get('ufile'):
                        attachment_value = {
                            'name': post['ufile'].filename,
                            'res_name': partner.name,
                            'res_model': 'res.partner',
                            'res_id': partner.id,
                            'datas': base64.encodestring(post['ufile'].read()),
                            'datas_fname': post['ufile'].filename,
                        }
                        env['ir.attachment'].create(attachment_value)
                #Stage 4: Additional info
                elif current_stage == 5:
                    value = {
                        'etat_art': post.get('etat_art'),
                        'objective': post.get('objective'),
                        'objectives': post.get('objectives'),
                        'fallout': post.get('fallout'),
                        'perspective': post.get('perspective'),
                    }
                    submission.write(value)
                    if post.get('ufile'):
                        attachment_value = {
                            'name': post['ufile'].filename,
                            'res_name': submission.name,
                            'res_model': 'project.submission',
                            'res_id': submission.id,
                            'datas': base64.encodestring(post['ufile'].read()),
                            'datas_fname': post['ufile'].filename,
                        }
                        env['ir.attachment'].create(attachment_value)
                        submission._get_attached_docs()
                #Stage 5: Tasks
                elif current_stage == 6 and post.get('to-save') == "1" and post.get('name') and post.get('type'):
                    value = {
                        'name': post.get('name'),
                        'type': post.get('type'),
                        'semester': post.get('semester'),
                        'objectives': post.get('objectives'),
                        'description': post.get('description'),
                        'partner': post.get('partner'),
                        'submission': submission.id,
                        'partners': [(6, 0, [int(x) for x in request.httprequest.form.getlist('partners')])],
                    }
                    if post.get('task_id') is not None:
                        task = env['project.submission.task'].browse(int(post.get('task_id')))
                        task.write(value)
                    else:
                        env['project.submission.task'].create(value)
                #Stage 6: Project budget informations
                elif current_stage == 7 and post.get('to-save') == "1" and post.get('type') and post.get('budget') and post.get('montant_propre'):
                    value = {
                        'type': post.get('type'),
                        'budget': post.get('budget'),
                        'montant_propre': float(post.get('montant_propre')),
                        'submission': submission.id,
                    }
                    if post.get('budgetline_id') is not None:
                        budgetline = env['project.submission.budgetline'].browse(int(post.get('budgetline_id')))
                        budgetline.write(value)
                    else:
                        env['project.submission.budgetline'].create(value)
        except ValidationError, e:
            next_stage = current_stage
            if post.get('partner_id'):
                post.update({'edit-partner': post.get('partner_id')})
            if post.get('task_id'):
                post.update({'edit-task': post.get('task_id')})
            if post.get('budgetline_id'):
                post.update({'edit-budgetline': post.get('budgetline_id')})
            env.cr.rollback()
            env.invalidate_all()
            error.update({'main': e.value})

        if next_stage == None:
            if bool(post) and post.get('submit') == 'next':
                next_stage = current_stage + 1
            elif bool(post) and post.get('submit') == 'prev':
                next_stage = current_stage - 1
            elif bool(post) and current_stage:
                next_stage = current_stage
            else:
                next_stage = 1
                
        #prepare next_stage vals
        vals = {
                'submission': submission,
                'error': error,
                'current_stage': next_stage,
                }
        if next_stage == 1:
            fields = env['project.offer.field'].search([])
            duration_steps = range(offer.min_time, offer.max_time + 1)
            vals.update({
                'error': error,
                'duration_steps': duration_steps,
                'fields': fields,
            })
        if next_stage == 2:
            vals.update({
                'error': error,
            })
        elif next_stage == 3 or next_stage == 4:
            if post.get('edit-partner'):
                partner = env['res.partner'].browse(int(post.get('edit-partner'))) if post.get('edit-partner') else env['res.partner'].browse(int(post.get('partner_id')))
                documents = env['ir.attachment'].search([('res_model', '=', 'res.partner'), ('res_id', '=', partner.id)])
                countries = env['res.country'].search()
                vals.update({
                    'partner': partner,
                    'documents': documents,
                    'countries': countries
                })
                
            if post.get('add-partner'):
                vals.update({'new': True})
            else:
                vals.update({'new': False})
            vals.update({
                'error': error,
                'partners': submission.partners.filtered(lambda p: p.category == ('scientifique' if next_stage == 3 else 'industriel'))
            })
        elif next_stage == 5:
            vals.update({
                'error': error,
            })
        elif next_stage == 6:
            types = env['project.submission.task.type'].search([])
            if post.get('edit-task'):
                task = env['project.submission.task'].browse(int(post.get('edit-task')))
                vals.update({'task': task})
            if post.get('add-task'):
                vals.update({'new': True})
            else:
                vals.update({'new': False})
            duration_steps = range(1, submission.duration + 1)
            vals.update({
                'duration_steps': duration_steps,
                'types': types,
                'error': error,
            })
        elif next_stage == 7:
            types = env['project.budgetline.type'].search([])
            if post.get('edit-budgetline'):
                budgetline = env['project.submission.budgetline'].browse(int(post.get('edit-budgetline')))
                vals.update({'budgetline': budgetline})
            if post.get('add-budgetline'):
                vals.update({'new': True})
            else:
                vals.update({'new': False})
            vals.update({
                'types': types,
                'error': error,
            })
        return request.render('website_project_submission.apply', vals)
# vim :et:
