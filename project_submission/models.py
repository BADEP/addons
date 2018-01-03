# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


AVAILABLE_PRIORITIES = [
    ('0', 'Bad'),
    ('1', 'Below Average'),
    ('2', 'Average'),
    ('3', 'Good'),
    ('4', 'Excellent')
]

SUBMISS_ETAT= [
    ('draft', 'Brouillon'),
    ('submitted', 'Soumis'),
    ('pending', 'En cours d\'étude'),
    ('accepted', 'Aprouvé'),
    ('rejected', 'Refusé')
]

REQSOUMISS_ETAT =[
    ('draft', 'Brouillon'),
    ('submitted', 'En cours'),
    ('accepted', 'Aprouvé'),
    ('rejected', 'Refusé'),
    ('cancel', 'Annulé')
]

class ProjectOffer(models.Model):
    """hr.job"""
    _description = u'Offre'
    _name = 'project.offer'
    _inherit = ['mail.thread']

    @api.one
    def _get_default_host(self):
        return self.env.user.company_id.partner_id.id
    
    @api.one
    def _get_default_manager(self):
        return self.env.user.id

    name = fields.Char(string='Nom', required=True)
    documents = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents sources')
    documents_count =  fields.Integer(compute='_count_all', string='Nombre de documents')
    host =  fields.Many2one('res.partner', 'Institut hôte',default=_get_default_host)
    submissions = fields.One2many('project.submission', 'offer', string='Soumissions')
    type = fields.Many2one('project.offer.type')
    survey =  fields.Many2one('survey.survey', 'Formulaire d\'inscription')
    color = fields.Integer('Couleur', default=0)
    state =  fields.Selection([('draft', 'Brouillon'), ('open', 'En cours'),
                              ('done', 'Terminé'), ('closed', 'Fermé')],
                              string='Status', readonly=True, required=True,
                              track_visibility='always', copy=False, default='draft')
    submissions_count =  fields.Integer(compute='_count_all', string='Soumissions')
    accepted_count =  fields.Integer(compute='_count_all', string='Soumissions acceptées')
    manager =  fields.Many2one('res.users', 'Responsable', track_visibility='always', default=_get_default_manager)
    date_open = fields.Datetime(string='Date de publication')
    date_closed = fields.Datetime(string='Date de clôture')
    min_time = fields.Integer(string='Durée minimale')
    max_time = fields.Integer(string='Durée maximale')
    budget_total = fields.Float('Budget', digits_compute=dp.get_precision('Account'))
    
    @api.constrains('min_time', 'max_time')
    def _check_min_max_time(self):
        if self.min_time > self.max_time:
            raise ValidationError("La durée minimale ne peut être inférieure à la durée maximale.")
    
    @api.one
    def _get_attached_docs(self):
        res = self.env['ir.attachment'].search([('res_model', '=', 'project.offer'), ('res_id', '=', self.id)])
        self.documents =  res.ids
    
    @api.cr_uid_ids_context
    def action_get_submission_tree_view(self, cr, uid, ids, context=None):
        #open attachments of job and related applicantions.
        model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project_submission', 'action_project_submission')
        action = self.pool.get(model).read(cr, uid, action_id, context=context)
        action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        action['domain'] = str([('offer', 'in', ids)])
        return action
     
    @api.cr_uid_ids_context
    def action_get_attachment_tree_view(self, cr, uid, ids, context=None):
        #open attachments of job and related applicantions.
        model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'action_attachment')
        action = self.pool.get(model).read(cr, uid, action_id, context=context)
        action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        action['domain'] = str([('res_model', '=', 'project.offer'), ('res_id', 'in', ids)])
        return action
    
    @api.multi
    def action_print_survey(self):
        if self.survey:
            return self.env['survey.survey'].browse(self.survey.id).action_print_survey()
    
    @api.one
    @api.depends('submissions')
    def _count_all(self):
        self.submissions_count = len(self.submissions)
        self.accepted_count = len(self.submissions.filtered(lambda s: s.state == 'accepted'))
        self.documents_count = len(self.documents)
        
    @api.one
    def action_open(self):
        self.state = 'open'
        self.date_open = fields.Datetime.now()
        
    @api.one
    def action_close(self):
        self.state = 'closed'
        self.date_closed = fields.Datetime.now()

class ProjectOfferField(models.Model):
    _name = 'project.offer.field'
    _description = u'Thématique'
    
    name = fields.Char('Nom')

class ProjectOfferType(models.Model):
    """hr.department"""
    _name = 'project.offer.type'
    _description = u'Type d\'appel à projets'
    
    name = fields.Char('Nom', required=True)
    offers = fields.One2many('project.offer', 'type')

class ProjectSubmission(models.Model):
    """hr.applicant"""
    _name = 'project.submission'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = u'Soumission'
    
    @api.one
    def _get_manager(self):
        return self.offer.user_id.id
    
    name = fields.Char('Intitulé du projet', required=True)
    acronyme = fields.Char('Acronyme', required=True)
    offer = fields.Many2one('project.offer', string='Offre de projet', required=True)
    candidate = fields.Many2one('project.candidate', string='Soumissionnaire', required=True)
    field = fields.Many2one('project.offer.field', 'Domaine d\'activité', required=True)
    partners = fields.One2many('project.submission.partner', 'submission', string='Partenaires')
    description = fields.Text('Description', required=True)
    manager = fields.Many2one('res.users', 'Responsable', default=_get_manager)
    date_submitted = fields.Datetime('Date de soumission', readonly=True)
    date_processed = fields.Datetime('Date de traitement', readonly=True)
    date_action = fields.Datetime('Date de la prochaine action')
    title_action = fields.Char('Prochaine action', size=64)
    partner_mobile = fields.Char(related='candidate.mobile', store=False)
    organisme = fields.Many2one('res.partner', related='candidate.parent_id', string='Organisme', store=False)
    project = fields.Many2one('project.project', string='Projet')
    state = fields.Selection(SUBMISS_ETAT, 'Etat', track_visibility='always', default='draft')
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Appréciation')
    color = fields.Integer('Couleur', default=0)
    documents = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents sources')
    documents_count =  fields.Integer(compute='_count_all', string='Nombre de documents')
    survey = fields.Many2one('survey.survey', related='offer.survey')
    response = fields.Many2one('survey.user_input', string="Réponse au formulaire")
    budget = fields.Float(compute='_get_amounts', store=True, digital_precision=dp.get_precision('Account'))
    montant_subventionne = fields.Float(compute='_get_amounts', string="Montant subventionné", store=True, digital_precision=dp.get_precision('Account'))
    montant_propre = fields.Float(compute='_get_amounts', string="Financement propre", store=True, digital_precision=dp.get_precision('Account'))
    percent_subventionne = fields.Float(compute='_get_amounts', digital_precision=2, string="Pourcentage subventionné (%)", store=True)
    budget_lines = fields.One2many('project.submission.budgetline', 'submission', string="Lignes de budget")
    duration = fields.Integer('Durée du projet')
    
    @api.one
    @api.constrains('duration')
    def _check_duration(self):
        if self.offer:
            if self.duration > self.offer.max_time:    
                raise ValidationError("La durée du prjet doit être inférieure à la durée maximum de l'offre: %s mois" % self.offer.max_time)
            if self.duration > self.offer.max_time or self.duration < self.offer.min_time:    
                raise ValidationError("La durée du prjet doit être supérieure à la durée minimum du projet: %S mois " % self.offer.min_time)
    
    @api.one
    @api.depends('budget_lines')
    def _get_amounts(self):
        self.budget = sum(self.budget_lines.mapped('budget'))
        self.montant_subventionne = sum(self.budget_lines.mapped('montant_subventionne'))
        self.montant_propre = sum(self.budget_lines.mapped('montant_propre'))
        self.percent_subventionne = (self.montant_subventionne / self.budget)*100 if self.budget != 0 else 0
  
    @api.multi
    def _get_attached_docs(self):
        res = {}
        for rec in self:
            res[rec.id] = self.env['ir.attachment'].search([('res_model', '=', 'project.submission'), ('res_id', '=', rec.id)])
        return res
        
    @api.cr_uid_ids_context
    def action_get_attachment_tree_view(self, cr, uid, ids, context=None):
        #open attachments of job and related applicantions.
        model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'action_attachment')
        action = self.pool.get(model).read(cr, uid, action_id, context=context)
        action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        action['domain'] = str([('res_model', '=', 'project.submission'), ('res_id', 'in', ids)])
        return action

    @api.one
    @api.depends('documents')
    def _count_all(self):
        self.documents_count = len(self.documents)
    
    @api.one
    def get_early_stage(self):
        if not (self.candidate.parent_id and self.candidate.function and self.candidate.mobile and self.candidate.email and self.duration):
            return 1
        elif not (self.partners):
            return 2
        elif not (self.budget_lines):
            return 3
        elif self.survey and (not self.response or (self.response and self.response.state!='done')):
            return 4
        return 5
    
    @api.multi
    def action_makeMeeting(self):
        
        partners= []
        if self.candidate:
            partners.append(self.candidate.partner_id.id)
        if self.user_id :
            partners.append(self.user_id.partner_id.id)
        else:
            partners.append(self.env.user.partner_id.id)
        res = self.env['ir.actions.act_window'].for_xml_id('calendar', 'action_calendar_event')
        res['context'] = {
            'default_partner_ids': partners,
            'default_user_id': self.user_id if self.user_id else self.env.user,
            'default_name': self.name,
        }
        return res
    
    @api.multi
    def action_start_survey(self):
        # create a response and link it to this applicant
        if self.survey:
            if not self.response:
                response = self.env['survey.user_input'].create({'survey_id': self.survey.id, 'partner_id': self.candidate.user.partner_id.id})
                self.write({'response': response.id})
            else:
                response = self.response
            return self.survey.with_context(survey_token = response.token).action_start_survey()
        return False

    @api.multi
    def action_print_survey(self):
        if not self.response:
            return self.survey.action_print_survey()
        else:
            return self.survey.with_context(survey_token = self.response.token).action_print_survey()

class ProjectSubmissionPartner(models.Model):
    _name = 'project.submission.partner'
    
    submission = fields.Many2one('project.submission')
    partner = fields.Many2one('res.partner', string='partenaire')
    
    type = fields.Many2one('project.partner.type')
    time = fields.Integer(string='Durée (mois)', required=True)
    montant = fields.Float(digital_precision=dp.get_precision('Account'), required=True, string='Financement demandé / mois')
    total = fields.Float(digital_precision=dp.get_precision('Account'), compute='_get_total', store=True)
    
    @api.one
    @api.depends('time', 'montant')
    def _get_total(self):
        self.total = self.time * self.montant

class ProjectPartnerType(models.Model):
    _name = 'project.partner.type'
    
    name = fields.Char(required=True)

class ProjectSubmissionBudgetLine(models.Model):
    _name = 'project.submission.budgetline'
    
    submission = fields.Many2one('project.submission', required=True, ondelete='cascade')
    budget = fields.Float(digital_precision=dp.get_precision('Account'), required=True)
    montant_propre = fields.Float(digital_precision=dp.get_precision('Account'), required=True)
    montant_subventionne = fields.Float(compute='_get_amount', store=True, digital_precision=dp.get_precision('Account'))
    percent_subventionne = fields.Float(compute='_get_amount', digital_precision=2, store=True)
    type = fields.Many2one('project.budgetline.type', required=True)
    
    _sql_constraints = [
        ('submission_type_unique',
         'unique(submission, type)',
         'Une seule ligne de budget est permise par type')
    ]
    
    @api.one
    @api.depends('budget', 'montant_propre')
    def _get_amount(self):
        self.montant_subventionne = self.budget - self.montant_propre
        self.percent_subventionne = (self.montant_subventionne / self.budget)*100 if self.budget != 0 else 0
    
    @api.one
    @api.constrains('budget', 'montant_propre')
    def _check_amounts(self):
        if self.budget < self.montant_propre:
            raise ValidationError("Le financement propre ne peut être supérieur au budget.")

class ProjectBudgetLineType(models.Model):
    _name = 'project.budgetline.type'
    
    name = fields.Char(required=True)

class ProjectCandidate(models.Model):

    """hr.employee"""
    _inherit = ['mail.thread']
    _inherits = {"res.users": 'user'}
    _name = 'project.candidate'
    _description = u'Soumissionaire'

    user = fields.Many2one('res.users', 'Utilisateur lié', required=True, ondelete='restrict')
    submissions = fields.One2many('project.submission', 'candidate', 'Soumissions')
    submissions_count =  fields.Integer(compute='_count_all', string='Soumissions')
    documents = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents sources')
    documents_count =  fields.Integer(compute='_count_all', string='Nombre de documents')
    color = fields.Integer('Color Index', default=0)
    
    @api.one
    def onchange_type(self, is_company):
        if self.user:
            return self.user.onchange_type(is_company)
    
    @api.one
    def onchange_address(self, use_parent_address, parent_id):
        if self.user:
            return self.user.onchange_address(use_parent_address, parent_id)
    @api.one
    def onchange_state(self, state_id):
        if self.user:
            return self.user.onchange_state(state_id)
    @api.one
    def action_reset_password(self):
        if self.user:
            return self.user.action_reset_password()
    
    @api.one
    def _count_all(self):
        self.documents_count = len(self.documents)
        self.submissions_count = len(self.submissions)
    
    @api.one
    def _get_attached_docs(self):
        res = self.env['ir.attachment'].search([('res_model', '=', 'project.candidate'), ('res_id', '=', self.id)])
        res2 = self.env['ir.attachment'].search([('res_model', '=', 'project.submission'), ('res_id', 'in', self.submissions.ids)])
        self.documents =  res.ids + res2.ids
    
    @api.cr_uid_ids_context
    def action_get_attachment_tree_view(self, cr, uid, ids, context=None):
        model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'action_attachment')
        action = self.pool.get(model).read(cr, uid, action_id, context=context)
        action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        action['domain'] = str([('res_model', '=', 'project.candidate'), ('res_id', 'in', ids)])
        return action
        
    @api.cr_uid_ids_context
    def action_get_submission_tree_view(self, cr, uid, ids, context=None):
        model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project_submission', 'action_project_submission')
        action = self.pool.get(model).read(cr, uid, action_id, context=context)
        action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        action['domain'] = str([('candidate', 'in', ids)])
        return action
    
class ProjectRequest(models.Model):  
    _name = 'project.request'
    _description = u'Demande de ressources'
    
    name = fields.Char(string='Objet', size=200)
    type_id = fields.Many2one('project.request.type', 'Type de demande')
    submission_id = fields.Many2one('project.submission', 'Projet')
    request_date = fields.Datetime('Date de demande', readonly=True)
    processing_date = fields.Datetime('Date de traitement', readonly=True)
    state = fields.Selection(REQSOUMISS_ETAT, 'Submission')
    note = fields.Text(required=True)

class ProjectRequestType(models.Model):
    _name = 'project.request.type'
    _description = 'Type de demande'
    
    name = fields.Char()
    
    