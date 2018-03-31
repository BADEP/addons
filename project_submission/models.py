# -*- coding: utf-8 -*-

from openerp import tools
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
try:
    from copyleaks.copyleakscloud import CopyleaksCloud
    from copyleaks.product import Product
    from processoptions import ProcessOptions
except ImportError:
    pass

AVAILABLE_PRIORITIES = [
    ('0', 'D'),
    ('1', 'C'),
    ('2', 'B'),
    ('3', 'A'),
    ('4', 'A+')
]

SUBMISS_ETAT= [
    ('draft', 'En cours de rédaction'),
    ('submitted', 'Soumis'),
    ('pending', 'Présélection IRESEN'),
    ('preselectedcs', 'Préselection CS'),
    ('preselectedcss', 'Préselection CSS'),
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

    def _get_default_host(self):
        return self.env.user.company_id.partner_id.id

    def _get_default_manager(self):
        return self.env.user.id

    name = fields.Char(string='Nom', required=True)
    category = fields.Selection([('innoproject', 'Inno-PROJECT'), ('innoboost', 'Inno-BOOST')])
    description = fields.Text(string='Description', translate=True)
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
    min_time = fields.Integer(string='Durée minimale (en semestres)')
    max_time = fields.Integer(string='Durée maximale (en semestres)')
    budget_total = fields.Float('Budget', digits_compute=dp.get_precision('Account'))
    task_types = fields.Many2many('project.submission.task.type')

    @api.constrains('min_time', 'max_time')
    def _check_min_max_time(self):
        if self.min_time > self.max_time:
            raise ValidationError("La durée minimale ne peut être inférieure à la durée maximale.")
    
    @api.one
    def _get_attached_docs(self):
        res = self.env['ir.attachment'].search([('res_model', '=', 'project.offer'), ('res_id', '=', self.id)])
        self.documents =  res.ids
     
    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0]}
        action['domain'] = str([('res_model', '=', 'project.offer'), ('res_id', 'in', self.ids)])
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
    
    name = fields.Char('Nom', translate=True)
    description = fields.Text(translate=True)

class ProjectOfferType(models.Model):
    _name = 'project.offer.type'
    _description = u'Type d\'appel à projets'
    
    name = fields.Char('Nom', required=True, translate=True)
    offers = fields.One2many('project.offer', 'type')

class ProjectSubmission(models.Model):
    """hr.applicant"""
    _name = 'project.submission'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = u'Soumission'
    
    @api.one
    @api.onchange('offer', 'offer.manager')
    def _get_default_manager(self):
        self.manager = self.offer.manager

    @api.depends('partners', 'candidate')
    @api.one
    def _get_possible_partners_values(self):
        self.all_partners = self.partners + self.candidate.partner_id

    name = fields.Char('Intitulé du projet', required=True)
    acronyme = fields.Char('Acronyme')
    offer = fields.Many2one('project.offer', string='Offre de projet', required=True)
    category = fields.Selection([('innoproject', 'Inno-PROJECT'), ('innoboost', 'Inno-BOOST')], related='offer.category', store=True)
    candidate = fields.Many2one('res.users', string='Soumissionnaire', required=True)
    partner = fields.Many2one('res.partner', related='candidate.partner_id', string='Fiche partenaire', required=True)
    inventor = fields.Many2one('res.partner', string='Inventeur')
    field_ids = fields.Many2many('project.offer.field', string='Thématiques')
    partners = fields.Many2many('res.partner', string='Partenaires')
    description = fields.Html('Description')
    etat_art = fields.Html('État de l’art')
    objective = fields.Html('Objectif global du projet')
    objectives = fields.Html('Objectifs spécifiques')
    fallout = fields.Html('Retombées attendues du projet')
    perspective = fields.Html('Perspectives d’application')
    produits_services_process = fields.Html('Produit/ Service / Process')
    analyse_macro = fields.Html('Analyse macro-environnementale')
    analyse_marche = fields.Html('Analyse du marché')
    cible = fields.Html('Cible')
    analyse_competitive = fields.Html('Analyse compétitive')
    proposition_valeur = fields.Html('Proposition de valeur pour le client')
    business_model = fields.Html('Business model initial')
    invest_retour = fields.Html('Investissement et retour sur investissement')
    plan = fields.Html('Plan du projet')
    trl = fields.Integer()
    
    n_related_publications = fields.Integer(string='Nombre de publications')
    n_ing_doc = fields.Integer(string='Nombre de doctorants/postdocs/ingénieurs')
    n_master_pfe = fields.Integer(string='Nombre de Masters et PFE')
    manager = fields.Many2one('res.users', 'Responsable')
    date_submitted = fields.Datetime('Date de soumission', readonly=True)
    date_processed = fields.Datetime('Date de traitement', readonly=True)
    date_action = fields.Datetime('Date de la prochaine action')
    title_action = fields.Char('Prochaine action', size=64)
    partner_mobile = fields.Char(related='candidate.mobile', store=False)
    organisme = fields.Many2one('res.partner', related='candidate.parent_id', string='Organisme', store=True)
    project = fields.Many2one('project.project', string='Projet')
    state = fields.Selection(SUBMISS_ETAT, 'Etat', track_visibility='always', default='draft')
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Appréciation')
    color = fields.Integer('Couleur', default=0)
    documents = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents sources')
    documents_count =  fields.Integer(compute='_count_all', string='Nombre de documents')
    all_documents = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents associés')
    all_documents_count =  fields.Integer(compute='_count_all', string='Nombre de documents')
    survey = fields.Many2one('survey.survey', related='offer.survey')
    response = fields.Many2one('survey.user_input', string="Réponse au formulaire")
    budget = fields.Float(compute='_get_amounts', store=False, digital_precision=dp.get_precision('Account'))
    montant_subventionne = fields.Float(compute='_get_amounts', string="Montant subventionné", store=False, digital_precision=dp.get_precision('Account'))
    montant_propre = fields.Float(compute='_get_amounts', string="Financement propre", store=False, digital_precision=dp.get_precision('Account'))
    percent_propre = fields.Float(compute='_get_amounts', digital_precision=2, string="Pourcentage propre (%)", store=False)
    budget_lines = fields.One2many('project.submission.budgetline', 'submission', string="Lignes de budget")
    personnels = fields.One2many('project.submission.personnel', 'submission', string="Personnels")
    duration = fields.Integer('Durée du projet (en semestres)')
    tasks = fields.One2many('project.submission.task', 'submission', string="Taches et livrables")
    keywords = fields.Char(string='Mots-clés')
    costs = fields.One2many('project.submission.cost', 'submission', string='Détail du coût du financement propre')
    all_partners = fields.Many2many(
        comodel_name='res.partner',
        compute='_get_possible_partners_values', readonly=True)
    
    """@api.one
    @api.depends('description')
    def _get_description_score(self):
        cloud = CopyleaksCloud(Product.Education, 'k.hazam@badep.ma', '9DE022AA-D59C-4785-8198-25B3909CD5BC')# You can change the product.
        options = ProcessOptions()
        options.setSandboxMode(True)  # Scan will not consume any credits and will return dummy results.
        options.setHttpCallback("http://yoursite.here/callback") # Recieve a completion callback with the results. For testing purposes we recommend using http://requestb.in
        process = cloud.createByText(self.description, options)
        [iscompleted, percents] = process.isCompleted()
        if iscompleted:
            self.description_score = process.getResults()"""
    
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
        self.percent_propre = (self.montant_propre / self.budget)*100 if self.budget != 0 else 0
  
    @api.one
    def _get_attached_docs(self):
        self.documents = self.env['ir.attachment'].search([('res_model', '=', 'project.submission'), ('res_id', '=', self.id)]).ids
        res1 = self.env['ir.attachment'].search([('res_model', '=', 'project.submission'), ('res_id', '=', self.id)])
        res2 = self.env['ir.attachment'].search([('res_model', '=', 'res.users'), ('res_id', '=', self.candidate.id)])
        res3 = self.env['ir.attachment'].search([('res_model', '=', 'res.partner'), ('res_id', 'in', self.partners.ids)])
        self.documents = res1.ids
        self.all_documents =  res1.ids + res2.ids + res3.ids
        
    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0]}
        action['domain'] = str([('res_model', '=', 'project.submission'), ('res_id', 'in', self.ids)])
        return action

    @api.multi
    def action_get_all_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0], 'search_default_group_by': 'parent_id'}
        action['domain'] = str(['|','|','&',('res_model', '=', 'project.submission'), ('res_id', '=', self.ids),'&',('res_model', '=', 'res.partner'), ('res_id', 'in', self.partners.ids),'&',('res_model', '=', 'res.users'), ('res_id', '=', self.candidate.id)])
        return action

    @api.one
    @api.depends('documents')
    def _count_all(self):
        self.documents_count = len(self.documents)
        self.all_documents_count = len(self.all_documents)
    
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
                response = self.env['survey.user_input'].create({'survey_id': self.survey.id, 'partner_id': self.candidate.partner_id.id})
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

class ProjectSubmissionCost(models.Model):
    _name = 'project.submission.cost'

    @api.depends('submission', 'submission.partners', 'submission.candidate')
    @api.one
    def _get_possible_partners_values(self):
        self.all_partners = self.submission.partners.filtered(lambda p: p.category == 'industriel')

    submission = fields.Many2one('project.submission')
    partner = fields.Many2one('res.partner', required=True, string='Partenaire', domain="[('id', 'in', all_partners[0][2])]", ondelete='cascade')
    type = fields.Many2one('project.budgetline.type', string='Rubrique')
    montant = fields.Float(default=0)
    all_partners = fields.Many2many(
        comodel_name='res.partner',
        compute='_get_possible_partners_values', readonly=True)
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    submissions = fields.Many2many('project.submission')
    category = fields.Selection([('scientifique', 'Scientifique'), ('industriel', 'Industriel')])
    documents_count =  fields.Integer(compute='_count_all', string='Nombre de soumissions')
    entite_recherche = fields.Char('Entité de recherche')
    partner_references = fields.Text('Références du partenaire')
    effectif = fields.Integer('Effectif global')
    effectif_chercheur = fields.Integer('Effectif de chercheurs')
    effectif_doc = fields.Integer('Effectif de doctorants')
    capital = fields.Float('Capital')
    cnss = fields.Char('CNSS')
    rc = fields.Char('Registre de commerce')
    ca = fields.Float('Chiffre d\'affaires')
    documents = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents sources')
    documents_count =  fields.Integer(compute='_count_all', string='Nombre de documents')
    submissions_count =  fields.Integer(compute='_count_all', string='Nombre de soumissions')

    @api.one
    def _count_all(self):
        self.documents_count = len(self.documents)
        self.submissions_count = len(self.submissions)
    
    @api.one
    def _get_attached_docs(self):
        res = self.env['ir.attachment'].search([('res_model', '=', 'res.partner'), ('res_id', '=', self.id)])
        self.documents =  res.ids

class ProjectPartnerFunction(models.Model):
    _name = 'project.partner.function'
    
    name = fields.Char(required=True, string='Nom', translate=True)
    is_scientifique = fields.Boolean(default=True, string='Scientifique')
    is_industriel = fields.Boolean(default=True, string='Industriel')

class ProjectSubmissionTask(models.Model):
    _name = 'project.submission.task'

    @api.one
    @api.onchange('submission', 'submission.candidate')
    def _get_default_partner(self):
        self.partner = self.submission.candidate.partner_id
        
    @api.depends('submission', 'submission.partners', 'submission.candidate')
    @api.one
    def _get_possible_partners_values(self):
        self.all_partners = self.submission.partners + self.submission.candidate.partner_id

    submission = fields.Many2one('project.submission')
    name = fields.Char(string='Designation', required=True)
    type = fields.Many2one('project.submission.task.type', required=True)
    semester = fields.Integer(string='Semestre')
    all_partners = fields.Many2many(
        comodel_name='res.partner',
        compute='_get_possible_partners_values', readonly=True)
    partner = fields.Many2one('res.partner', string='Responsable', domain="[('id', 'in', all_partners[0][2])]", ondelete='cascade')
    partners = fields.Many2many('res.partner', string='Partenaires impliquées', domain="[('id', 'in', all_partners[0][2])]")
    objectives = fields.Text(string='Objectifs')
    description = fields.Text(string='Description des tâches et rôles des partenaires')
    lots = fields.One2many('project.submission.lot', 'task', string='Livrables')
    
class ProjectSubmissionTaskType(models.Model):
    _name = 'project.submission.task.type'
    
    name = fields.Char('Nom', required=True, translate=True)
    
class ProjectSubmissionLot(models.Model):
    _name = 'project.submission.lot'
    
    task = fields.Many2one('project.submission.task')
    name = fields.Char('Nom', required=True)
    month_due = fields.Integer(string='Mois d\'échéance')
    type = fields.Many2one('project.lot.type', required=True)
    
class ProjectLotType(models.Model):
    _name = 'project.lot.type'
    
    name = fields.Char('Nom', required=True, translate=True)

class ProjectSubmissionPersonnel(models.Model):
    _name = 'project.submission.personnel'
    
    submission = fields.Many2one('project.submission')
    
    type = fields.Selection([('scientifique', 'Scientifique'), ('industriel', 'Industriel')], required=True)
    function = fields.Many2one('project.partner.function', string='Titre')
    number = fields.Integer(string='Effectif', default=0)
    time = fields.Integer(string='Durée (mois)', required=True, default=0)
    montant_propre = fields.Float(digital_precision=dp.get_precision('Account'), required=True, string='Financement propre / mois', default=0)
    montant_demande = fields.Float(digital_precision=dp.get_precision('Account'), required=True, string='Financement demandé / mois', default=0)
    total = fields.Float(digital_precision=dp.get_precision('Account'), compute='_get_total', store=True)
    
    @api.one
    @api.depends('time', 'montant_propre', 'montant_demande')
    def _get_total(self):
        self.total = self.time * (self.montant_propre + self.montant_demande)

class ProjectSubmissionBudgetLine(models.Model):
    _name = 'project.submission.budgetline'
    
    submission = fields.Many2one('project.submission', required=True, ondelete='cascade')
    montant_subventionne = fields.Float(digital_precision=dp.get_precision('Account'), required=True, default=0)
    montant_propre = fields.Float(digital_precision=dp.get_precision('Account'), required=True, default=0)
    budget = fields.Float(compute='_get_amount', store=True, digital_precision=dp.get_precision('Account'))
    percent_propre = fields.Float(compute='_get_amount', digital_precision=2, store=True, string='Pourcentage propre')
    type = fields.Many2one('project.budgetline.type', required=True)
    
    _sql_constraints = [
        ('submission_type_unique',
         'unique(submission, type)',
         'Une seule ligne de budget est permise par type')
    ]
    
    @api.one
    @api.depends('montant_subventionne', 'montant_propre')
    def _get_amount(self):
        self.budget = self.montant_subventionne + self.montant_propre
        self.percent_propre = (self.montant_propre / self.budget)*100 if self.budget != 0 else 0

class ProjectBudgetLineType(models.Model):
    _name = 'project.budgetline.type'
    
    name = fields.Char(required=True, translate=True)

class ResUser(models.Model):
    _inherit = ['res.users']

    submissions = fields.One2many('project.submission', 'candidate', 'Soumissions')
    submissions_count =  fields.Integer(compute='_count_all', string='Soumissions')
    self_documents = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents sources')
    documents = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents sources')
    documents_count =  fields.Integer(compute='_count_all', string='Nombre de documents')
    color = fields.Integer('Color Index', default=0)
    
    @api.one
    def _count_all(self):
        self.documents_count = len(self.documents)
        self.submissions_count = len(self.submissions)
    
    @api.one
    def _get_attached_docs(self):
        res = self.env['ir.attachment'].search([('res_model', '=', 'res.users'), ('res_id', '=', self.id)])
        res2 = self.env['ir.attachment'].search([('res_model', '=', 'project.submission'), ('res_id', 'in', self.submissions.ids)])
        self.self_documents = res.ids
        self.documents =  res.ids + res2.ids
    
    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0]}
        action['domain'] = str(['|', '&', ('res_model', '=', 'res.users'), ('res_id', 'in', self.ids), '&', ('res_model', '=', 'project.submission'), ('res_id', 'in', self.submissions.ids)])
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
    
    name = fields.Char(translate=True)
    
    
