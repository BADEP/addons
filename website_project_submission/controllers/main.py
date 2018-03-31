# -*- coding: utf-8 -*-
import base64
import time
from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request

from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.website.models.website import slug
from openerp.exceptions import ValidationError
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.addons.web.controllers.main import ensure_db
from openerp.addons.website_portal.controllers.main import WebsiteAccount

class PortalSubmissionWebsiteAccount(WebsiteAccount):
    
    
    @http.route(['/my/home/submissions'], type='http', auth="user", website=True)
    def submissions(self, **kw):
        submissions = {'submissions': request.env.user.submissions}
        #open_offers = 
        return request.website.render(
            'website_project_submission.submissions_only', submissions)

    @http.route(['/my/home'], type='http', auth="user", website=True)
    def account(self, **kw):
        response = super(PortalSubmissionWebsiteAccount, self).account(**kw)
        response.qcontext.update({
            'submissions': request.env.user.submissions,
        })
        return response
#        if post.get('unlink-submission'):
#            submission = request.env.submissions.filtered(lambda s: s.id == post.get('unlink-submission'))
    @http.route(['/my/home/delete/<model("project.submission"):submission>',
                 ], type='http', auth="public", website=True)
    def unlink_submission(self, submission=None, **post):
        submission and submission.unlink()
        return request.redirect("/my/home")

    
    @http.route(['/my/submissions/<int:submission_id>'], type='http', auth="user", website=True)
    def submissions_followup(self, submission_id=None):
        submission = request.env.user.submissions.filtered(lambda s: s.id == submission_id)
        if not submission:
            return request.website.render("website.404")
        return request.website.render("website_portal_sale.submissions_followup", {
            'submission': submission,
        })

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

class WebsiteProjectSubmission(http.Controller):


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
                 '/offers/apply/<model("project.offer"):offer>/<string:is_new>',
                 '/offers/apply/<model("project.offer"):offer>/stage/<int:next_stage>',
                 '/offers/apply/<model("project.offer"):offer>/submission/<model("project.submission"):submission>',
                 '/offers/apply/<model("project.offer"):offer>/submission/<model("project.submission"):submission>/stage/<int:next_stage>'
                 ], type='http', auth="public", website=True)
    def offers_apply(self, offer=None, next_stage=None, submission=None, is_new=None, **post):
        
        #If no user connected, force connection
        #TODO: Redirect to submission page if offer variable is in session
        if not request.session.uid:
            request.session.update({'offer': offer.id})
            return login_redirect()
            
        #Get the candidate, if no candidate create one
        sudo_env = request.env(user=SUPERUSER_ID)
        env = request.env()
        candidate = env.user

        #Get the submission, if no submission call creation template
        if not submission:
            if request.session.get('submission'):
                submission = candidate.submissions.filtered(lambda s: s.id == int(request.session.get('submission')))
            if not submission or is_new == 'new':
                submission = env['project.submission'].create({
                                                           'name': '/',
                                                           'offer': offer.id,
                                                           'candidate': candidate.id,})
        error = {}
        request.session.update({'submission': submission.id})
        #Save the current stage
        current_stage = post.get('current_stage') and int(post.get('current_stage'))
        try:
            if bool(post) and post.get('submit') != 'cancel':
                if post.get('unlink-doc'):
                    #TODO: call with adequate access right. Sudo might e dangerous if the id passed is wrong
                    sudo_env['ir.attachment'].browse(int(post.get('unlink-doc'))).unlink()
                if post.get('unlink-task'):
                    submission.tasks.filtered(lambda t: t.id == int(post.get('unlink-task'))).unlink()
                if post.get('unlink-partner'):
                    submission.costs.filtered(lambda c: c.partner.id == int(post.get('unlink-partner'))).unlink()
                    submission.write({'partners': [(3, int(post.get('unlink-partner')))]})
                    partner = sudo_env['res.partner'].browse(int(post.get('unlink-partner')))
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
                        'trl': post.get('trl'),
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
                    if post.get('organisme'):
                        if candidate.parent_id:
                            candidate.parent_id.write({'name': post.get('organisme')})
                        else:
                            organisme = sudo_env['res.partner'].create({'name': post.get('organisme')})
                            candidate.write({'parent_id': organisme.id})
                    else:
                        if candidate.parent_id:
                            part = candidate.parent_id
                            candidate.parent_id = False
                            """try:
                                part.unlink()
                            except Exception:
                                pass"""
                    if post.get('inventor'):
                        inventor_value = {
                            'name': post.get('inventor'),
                            'phone': post.get('inventor_phone'),
                            'mobile': post.get('inventor_mobile'),
                            'email': post.get('inventor_email'),
                        }
                        if submission.inventor:
                            submission.inventor.write(inventor_value)
                        else:
                            inventor = sudo_env['res.partner'].create(inventor_value)
                            submission.write({'inventor': inventor.id})
                    else:
                        if submission.inventor:
                            part = submission.inventor
                            submission.inventor = False
                            """try:
                                part.unlink()
                            except Exception:
                                pass"""
                    if post.get('ufile'):
                        for file in request.httprequest.files.getlist('ufile'):
                            attachment_value = {
                                'name': file.filename,
                                'res_name': value['name'],
                                'res_model': 'res.users',
                                'res_id': candidate.id,
                                'datas': base64.encodestring(file.read()),
                                'datas_fname': file.filename,
                            }
                            env['ir.attachment'].create(attachment_value)
                        candidate._get_attached_docs()
    
                #Stage 3: Project partners informations
                elif (current_stage == 3 or current_stage == 4) and post.get('to-save') == "1" and post.get('name'):
                    #partner_organisme = env['res.partner'].create({'name': post.get('organisme')})
                    category_id = False
                    if post.get('category_id'):
                        category_id = env['res.partner.category'].search([('name', '=', post.get('category_id'))])
                        if not category_id:
                            category_id = env['res.partner.category'].create({'name': post.get('category_id')})
                    partner_value = {
                        'name': post.get('name') and post.get('name'),
                        'country_id': post.get('partner_country') and post.get('partner_country'),
                        'is_company': True,
                        'city': post.get('city') and post.get('city'),
                        'zip': post.get('zip') and post.get('zip'),
                        'street': post.get('street') and post.get('street'),
                        'street2': post.get('street2') and post.get('street2'),
                        'email': post.get('email') and post.get('email'),
                        'phone': post.get('phone') and post.get('phone'),
                        'fax': post.get('fax') and post.get('fax'),
                        'website': post.get('website') and post.get('website'),
                        'cnss': post.get('cnss') and post.get('cnss'),
                        'ca': post.get('ca') and post.get('ca'),
                        'capital': post.get('capital') and post.get('capital'),
                        'partner_references': post.get('partner_references') and post.get('partner_references'),
                        'rc': post.get('rc') and post.get('rc'),
                        'category_id': category_id and [(6, 0, [category_id.id])],
                        'title': post.get('title') and post.get('title'),
                        'date': post.get('date') != '' and post.get('date'),
                        'effectif_doc': post.get('effectif_doc') and post.get('effectif_doc'),
                        'effectif': post.get('effectif') and post.get('effectif'),
                        'effectif_chercheur': post.get('effectif_chercheur') and post.get('effectif_chercheur'),
                        'entite_recherche': post.get('entite_recherche') and post.get('entite_recherche'),
                        #'parent_id': partner_organisme.id,
                        'category': 'scientifique' if current_stage == 3 else 'industriel',
                        'submissions': [(4, submission.id)]
                    }
                    if post.get('partner_id') is not None:
                        partner = sudo_env['res.partner'].browse(int(post.get('partner_id')))
                        partner.write(partner_value)
                    else:
                        partner = sudo_env['res.partner'].create(partner_value)
                    contact_value = {
                        'name': post.get('contact_name'),
                        'function': post.get('contact_function'),
                        'phone': post.get('contact_phone'),
                        'email': post.get('contact_email'),
                        'parent_id': partner.id,
                        'category': 'scientifique' if current_stage == 3 else 'industriel'
                    }
                    if partner.child_ids.ids:
                        partner.child_ids[0].write(contact_value)
                    else:
                        sudo_env['res.partner'].create(contact_value)
                    if post.get('ufile'):
                        for file in request.httprequest.files.getlist('ufile'):
                            attachment_value = {
                                'name': file.filename,
                                'res_name': partner.name,
                                'res_model': 'res.partner',
                                'res_id': partner.id,
                                'datas': base64.encodestring(file.read()),
                                'datas_fname': file.filename,
                            }
                            sudo_env['ir.attachment'].create(attachment_value)
                #Stage 4: Additional info
                elif current_stage == 5:
                    value = {
                        'etat_art': post.get('etat_art'),
                        'objective': post.get('objective'),
                        'objectives': post.get('objectives'),
                        'fallout': post.get('fallout'),
                        'perspective': post.get('perspective'),
                        'produits_services_process': post.get('produits_services_process'),
                        'analyse_macro': post.get('analyse_macro'),
                        'analyse_marche': post.get('analyse_marche'),
                        'cible': post.get('cible'),
                        'analyse_competitive': post.get('analyse_competitive'),
                        'proposition_valeur': post.get('proposition_valeur'),
                        'business_model': post.get('business_model'),
                        'invest_retour': post.get('invest_retour'),
                        'plan': post.get('plan'),
                    }
                    submission.write(value)
                    if post.get('ufile'):
                        for file in request.httprequest.files.getlist('ufile'):
                            attachment_value = {
                                'name': file.filename,
                                'res_name': submission.name,
                                'res_model': 'project.submission',
                                'res_id': submission.id,
                                'datas': base64.encodestring(file.read()),
                                'datas_fname': file.filename,
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
                elif current_stage == 7:
                    for line in submission.budget_lines:
                        vals = {
                            'montant_propre': post.get(str(line.id)+'montant_propre') and float(post.get(str(line.id)+'montant_propre')),
                            'montant_subventionne': post.get(str(line.id)+'montant_subventionne') and float(post.get(str(line.id)+'montant_subventionne'))
                        }
                        line.write(vals)
                    for line in submission.personnels:
                        vals = {
                            'time': post.get(str(line.id) + 'time') and int(post.get(str(line.id) + 'time')),
                            'number': post.get(str(line.id) + 'number') and float(post.get(str(line.id) + 'number')),
                            'montant_propre': post.get(str(line.id)+'montant_propre_personnel') and float(post.get(str(line.id) + 'montant_propre_personnel')),
                            'montant_demande': post.get(str(line.id)+'montant_demande_personnel') and float(post.get(str(line.id) + 'montant_demande_personnel'))
                        }
                        line.write(vals)
                    for line in submission.costs:
                        vals = {
                            'montant': post.get(str(line.id)+'montant_cout') and float(post.get(str(line.id) + 'montant_cout'))
                        }
                        line.write(vals)
                    
                elif current_stage == 8:
                    
                    if post.get('ufile'):
                        attachment_value = {
                            'name': str(time.time()) + '_' + post['ufile'].filename,
                            'res_name': submission.name,
                            'res_model': 'project.submission',
                            'res_id': submission.id,
                            'datas': base64.encodestring(post['ufile'].read()),
                            'datas_fname': post['ufile'].filename,
                            'parent_id': sudo_env['document.directory'].search([('name', '=', 'Conventions')]) and sudo_env['document.directory'].search([('name', '=', 'Conventions')]).ids[0]
                        }
                        sudo_env['ir.attachment'].create(attachment_value)
                    if post.get('submit') == 'confirm':
                        submission.state = 'submitted'
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
            vals.update({
                'error': error,
            })
        if next_stage == 2:
            vals.update({
                'error': error,
            })
        elif next_stage == 3 or next_stage == 4:
            if post.get('edit-partner'):
                partner = sudo_env['res.partner'].browse(int(post.get('edit-partner'))) if post.get('edit-partner') else env['res.partner'].browse(int(post.get('partner_id')))
                documents = sudo_env['ir.attachment'].search([('res_model', '=', 'res.partner'), ('res_id', '=', partner.id)])
                vals.update({
                    'partner': partner,
                    'documents': documents
                })
            if post.get('add-partner'):
                vals.update({'new': True})
            else:
                vals.update({'new': False})
            vals.update({
                'error': error
            })
        elif next_stage == 5:
            vals.update({
                'error': error,
            })
        elif next_stage == 6:
            if post.get('edit-task'):
                task = env['project.submission.task'].browse(int(post.get('edit-task')))
                vals.update({'task': task})
            if post.get('add-task'):
                vals.update({'new': True})
            else:
                vals.update({'new': False})
            vals.update({
                'error': error,
            })
        elif next_stage == 7:
            types = env['project.budgetline.type'].search([])
            missing_types = types - submission.budget_lines.mapped('type')
            for missing_type in missing_types:
                env['project.submission.budgetline'].create({
                    'submission': submission.id,
                    'type': missing_type.id
                })
            scientifique_functions = env['project.partner.function'].search([('is_scientifique', '=', True)])
            missing_scientifique_functions = scientifique_functions - submission.personnels.filtered(lambda p: p.type == 'scientifique').mapped('function')
            for missing_function in missing_scientifique_functions:
                env['project.submission.personnel'].create({
                    'type': 'scientifique',
                    'function': missing_function.id,
                    'submission': submission.id,
                })
            industriel_functions = env['project.partner.function'].search([('is_industriel', '=', True)])
            missing_industriel_functions = industriel_functions - submission.personnels.filtered(lambda p: p.type == 'industriel').mapped('function')
            for missing_function in missing_industriel_functions:
                env['project.submission.personnel'].create({
                    'type': 'industriel',
                    'function': missing_function.id,
                    'submission': submission.id,
                })
            
            partners = submission.partners.filtered(lambda p: p.category == 'industriel')
            for partner in partners:
                for t in types:
                    if len(submission.costs.filtered(lambda c: c.partner == partner and c.type == t)) == 0:
                        env['project.submission.cost'].create({
                            'partner': partner.id,
                            'type': t.id,
                            'submission': submission.id
                        })
            vals.update({
                'error': error,
            })
        elif next_stage == 8:
            error.update({
                'stage1': {
                    'Intitulé du projet' if env.lang == 'fr_FR' else 'Project Name': submission.name == '' or submission.name == '/',
                    'Acronyme du projet' if env.lang == 'fr_FR' else 'Project Acronym': submission.acronyme == '',
                    'Thématiques' if env.lang == 'fr_FR' else 'Themes': len(submission.field_ids) == 0,
                    'Durée du projet' if env.lang == 'fr_FR' else 'Project Duration': submission.duration == 0,
                    'Description du projet' if env.lang == 'fr_FR' else 'Project Description': submission.description == '',
                    'Nombre de publications' if env.lang == 'fr_FR' else 'Number of Publications': offer.category == 'innoproject' and submission.n_related_publications == 0,
                    'TRL' if env.lang == 'fr_FR' else 'Technological Readiness Level': offer.category == 'innoboost' and submission.trl == 0,
                    'Nombre de doctorants/postdocs/ingénieurs' if env.lang == 'fr_FR' else 'Number of PhD students/postdocs/engineers': submission.n_ing_doc == 0,
                    'Nombre d\'étudiants en Master et PFE' if env.lang == 'fr_FR' else 'Number of Master students and End of Studies projects': submission.n_master_pfe == 0,
                    'mots-clés' if env.lang == 'fr_FR' else 'Keywords': submission.keywords == '',
                },
                'stage2': {
                    'Nom du coordinateur/porteur du projet' if env.lang == 'fr_FR' else 'Coordinator/Promoter Full name': candidate.name == '',
                    'Etablissement' if env.lang == 'fr_FR' else 'Entreprise': candidate.parent_id.id == False,
                    'Fonction'if env.lang == 'fr_FR' else 'Function': candidate.function == '',
                    'Téléphone'if env.lang == 'fr_FR' else 'Phone': candidate.phone == '',
                    'Mobile': candidate.mobile == '',
                    'Email': candidate.email == '',
                    'Inventeur: Nom'if env.lang == 'fr_FR' else 'Inventor\'s Full Name': offer.category == 'innoboost' and (not submission.inventor or submission.inventor.name == ''),
                    'Inventeur: Téléphone'if env.lang == 'fr_FR' else 'Inventor\'s Phone': offer.category == 'innoboost' and (not submission.inventor or submission.inventor.phone == ''),
                    'Inventeur: Mobile 'if env.lang == 'fr_FR' else 'Inventor\'s Mobile': offer.category == 'innoboost' and (not submission.inventor or submission.inventor.mobile == ''),
                    'Inventeur: Email' if env.lang == 'fr_FR' else 'Inventor\s Email': offer.category == 'innoboost' and (submission.inventor == False or submission.inventor.email == ''),
                    'CV/Patentes' if env.lang == 'fr_FR' else 'CV/patents': (offer.category == 'innoproject' and candidate.documents_count < 6) or (offer.category == 'innoboost' and candidate.documents_count < 2),
                },
                'stage3': {
                    'Parenaires scientifiques' if env.lang == 'fr_FR' else 'Scientific Partners': len(submission.partners.filtered(lambda p: p.category=='scientifique')) == 0,
                    'Pièces jointes' if env.lang == 'fr_FR' else 'Attachments': any([p.documents_count == 0 for p in submission.partners.filtered(lambda p: p.category=='scientifique')]),
                },
                'stage4': {
                    'Partenaires industriels' if env.lang == 'fr_FR' else 'Industrial Partners': len(submission.partners.filtered(lambda p: p.category=='industriel')) == 0,
                    'Pièces jointes' if env.lang == 'fr_FR' else 'Attachments': any([p.documents_count == 0 for p in submission.partners.filtered(lambda p: p.category=='industriel')]),
                },
                'stage5': {
                    'Etat de l\'art' if env.lang == 'fr_FR' else 'State of the art': offer.category == 'innoproject' and submission.etat_art == '',
                    'Objectif global' if env.lang == 'fr_FR' else 'Overall objective': offer.category == 'innoproject' and submission.objective == '',
                    'Objectifs spécifiques' if env.lang == 'fr_FR' else 'Specific objectives': offer.category == 'innoproject' and submission.objectives == '',
                    'Perspective' if env.lang == 'fr_FR' else 'Perspective': offer.category == 'innoproject' and submission.perspective == '', 
                    submission._fields['fallout'].string: submission.fallout == '',
                    submission._fields['produits_services_process'].string: offer.category == 'innoboost' and submission.produits_services_process == '',
                    submission._fields['analyse_macro'].string: offer.category == 'innoboost' and submission.analyse_macro == '',
                    submission._fields['analyse_marche'].string: offer.category == 'innoboost' and submission.analyse_marche == '',
                    submission._fields['cible'].string: offer.category == 'innoboost' and submission.cible == '',
                    submission._fields['analyse_competitive'].string: offer.category == 'innoboost' and submission.analyse_competitive == '',
                    submission._fields['proposition_valeur'].string: offer.category == 'innoboost' and submission.proposition_valeur == '',
                    submission._fields['business_model'].string: offer.category == 'innoboost' and submission.business_model == '',
                    submission._fields['invest_retour'].string: offer.category == 'innoboost' and submission.invest_retour == '',
                    submission._fields['plan'].string: offer.category == 'innoboost' and submission.plan == '',
                    'Présentation du projet': len(submission.documents.filtered(lambda d: not d.parent_id)) == 0
                },
                'stage6': {
                    submission._fields['tasks'].string: len(submission.tasks) == 0,
                    },
                'stage7': {
                    submission._fields['budget'].string: submission.budget == 0,
                    #'Le pourcentage prôpre doit être supérieur à 30%': submission.percent_propre < 30,
                    submission._fields['personnels'].string: len(submission.personnels) == 0,
                    },
                'stage8': {
                    'Convention de collaboration': len(submission.documents.filtered(lambda d: d.parent_id.name == 'Conventions')) == 0,
                    }
            })
            vals.update({
                'error': error,
            })
            
        return request.render('website_project_submission.apply', vals)
# vim :et:
