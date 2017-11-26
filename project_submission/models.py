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
from openerp.modules.module import get_module_resource


AVAILABLE_PRIORITIES = [
    ('0', 'Bad'),
    ('1', 'Below Average'),
    ('2', 'Average'),
    ('3', 'Good'),
    ('4', 'Excellent')
]

SUBMISS_ETAT= [
    ('0', 'Brouillon'),
    ('1', 'Soumis'),
    ('2', 'En cours d étude'),
    ('3', 'Aprouvé'),
    ('4', 'Refusé')
]

REQSOUMISS_ETAT =[
    ('0', 'Brouillon'),
    ('1', 'En Cours'),
    ('2', 'Approuved'),
    ('3', 'Resused'),
    ('4', 'Annuler')
]

class ProjectSubmission(models.Model):
    """hr.applicant"""
    _name = 'project.submission'
    _order = "priority desc, id desc"
    
    name = fields.Char('Subject / Project Name', required=True)
    company_id = fields.Many2one('res.company', 'Company')
    domain_id = fields.Many2one('Project.field', 'Domain')
    state_id = fields.Many2one('res.country.state', 'State')
    country_id = fields.Many2one('res.country', 'Country')
    
    document_ids =  fields.Function(_get_attached_docs, type='One2many', relation='ir.attachment', string='Submissions')
    documents_count =  fields.Function(_count_all, type='Integer', string='Documents', multi=True)
    project = fields.Many2one('project.project', string='Projet')
    etat = fields.selection(SUBMISS_ETAT, 'Submission')
   
   
    categ_ids = fields.many2many('project.submission_category', string='Tags')

    """offer = fields.Many2one('project.offer', string='Offre projet')
    candidate = fields.Many2one('project.candidate')"""
    
    active = fields.boolean('Active', help="If the active field is set to false, it will allow you to hide the case without removing it.")
    description = fields.Text('Description')
    email_from = fields.Char('Email', size=128, help="These people will receive email.")
    email_cc = fields.Text('Watchers Emails', size=252, help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    probability = fields.Float('Probability')
    partner_id = fields.Many2one('res.partner', 'Contact')
    create_date = fields.Datetime('Creation Date', readonly=True, select=True)
    
    user_id = fields.Many2one('res.users', 'Responsible', track_visibility='onchange')
    date_closed = fields.Datetime('Closed', readonly=True, select=True)
    date_open = fields.Datetime('Assigned', readonly=True, select=True)
    date_action = fields.date('Next Action Date')
    title_action = fields.Char('Next Action', size=64)
    partner_phone = fields.Char('Phone', size=32)
    partner_mobile = fields.Char('Mobile', size=32)
    type_id = fields.Many2one('hr.recruitment.degree', 'Degree')
    
    _defaults = {
        'active': lambda *a: 1,
        'user_id': lambda s, cr, uid, c: uid,
        'stage_id': lambda s, cr, uid, c: s._get_default_stage_id(cr, uid, c),
        'categ_ids': lambda s, cr, uid, c: s._get_default_categ_ids(cr, uid, c),
        'company_id': lambda s, cr, uid, c: s._get_default_company_id(cr, uid, s._get_default_categ_ids(cr, uid, c), c),
        'color': 0,
        'priority': '0',
    }
    
    
class ProjectOffer(models.Model):
    """hr.job"""
    _name = 'project.offer'
    
    
    document_ids =  fields.Function(_get_attached_docs, type='One2many', relation='ir.attachment', string='Submission')
    documents_count =  fields.Function(_count_all, type='Integer', string='Documents', multi=True)
    address_id =  fields.Many2one('res.partner', 'Offer Location', help="Address where Candidat are working")
    submissions = fields.One2many('project.offer', 'offer', string='Candidatures')
    
    type = fields.Many2one('project.type')
    
    dureeRealisation = fields.Integer('Durée de Réalisation')
    
    formulaire_id =  fields.Many2one('survey.survey', 'Interview Form', 
                                 help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job")
    
    color = fields.Integer('Color Index')
    
    state =  fields.Selection([('Projet open', 'Projet Closed'), ('recruit', 'Projet in Progress')],
                                  string='Status', readonly=True, required=True,
                                  track_visibility='always', copy=False,
                                  help="By default 'Closed', set it to 'In Submission' if Soumissionnaire process is going on for this offer position.")
    
    """alias_id =  fields.Many2one('mail.alias', 'Alias', ondelete="restrict", required=True, help="Email alias for this job position. New emails will automatically "
                                         "create new applicants for this job position."),
    application_ids = fields.One2many('project.submission', 'job_id', 'Applications')
    application_count =  fields.Function(_count_all, type='Integer', string='Applications', multi=True)
    manager_id = fields.Related('department_id', 'manager_id', type='Many2one', string='Department Manager', relation='project.candidate', readonly=True, store=True),
    user_id =  fields.Many2one('res.users', 'Recruitment Responsible', track_visibility='onchange'),
    """
    
    _defaults = {
        'company_id': lambda self, cr, uid, ctx=None: self.pool.get('res.company')._company_default_get(cr, uid, 'project.offer', conText=ctx),
        'state': 'open',
    }
    

    def _address_get(self, cr, uid, conText=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, conText=conText)
        return user.company_id.partner_id.id

    _defaults = {
        'address_id': _address_get
    }
    
    
    
    def _auto_init(self, cr, conText=None):
        """Installation hook to create aliases for all jobs and avoid constraint errors."""
        return self.pool.get('mail.alias').migrate_to_alias(cr, self._name, self._table, super(ProjectOffer, self)._auto_init,
            'project.submission', self._columns['alias_id'], 'name', alias_prefix='offer+', alias_defaults={'offer_id': 'id'}, conText=conText)

    def create(self, cr, uid, vals, conText=None):
        alias_conText = dict(conText, alias_model_name='project.submission', alias_parent_model_name=self._name)
        offer_id = super(ProjectOffer, self).create(cr, uid, vals, conText=alias_conText)
        offer = self.browse(cr, uid, offer_id, conText=conText)
        self.pool.get('mail.alias').write(cr, uid, [offer.alias_id.id], {'alias_parent_thread_id': ProjectOffer, "alias_defaults": {'offer_id': offer_id}}, conText)
        return offer_id
    
    def unlink(self, cr, uid, ids, conText=None):
        # Cascade-delete mail aliases as well, as they should not exist without the job position.
        mail_alias = self.pool.get('mail.alias')
        alias_ids = [offer.alias_id.id for offer in self.browse(cr, uid, ids, conText=conText) if offer.alias_id]
        res = super(ProjectOffer, self).unlink(cr, uid, ids, conText=conText)
        mail_alias.unlink(cr, uid, alias_ids, conText=conText)
        return res

    def action_print_survey(self, cr, uid, ids, conText=None):
        offer = self.browse(cr, uid, ids, conText=conText)[0]
        survey_id = offer.survey_id.id
        return self.pool.get('survey.survey').action_print_survey(cr, uid, [survey_id], conText=conText)

    def set_open(self, cr, uid, ids, conText=None):
        self.write(cr, uid, ids, {
            'state': 'open',
            'no_of_Soumiss': 0,
            'no_of_hired_Candidat': 0
        }, conText=conText)
        return True
      
    
class ProjectType(models.Model):
    """hr.department"""
    _name = 'project.type'
    
    name = fields.Char('Libellé', required=True)
    offers = fields.One2many('project.offer', 'type')
    note = fields.Text('Note')
    
    manager_id = fields.Many2one('project.candidate', 'Manager')
    
    """complete_name = fields.Function(_dept_name_get_fnc, type="Char", string='Name')
    company_id = fields.Many2one('res.company', 'Company', select=True, required=False)
    parent_id = fields.Many2one('hr.department', 'Parent Department', select=True)
    child_ids = fields.One2many('hr.department', 'parent_id', 'Child Departments')
    
    member_ids = fields.One2many('project.candidate', 'department_id', 'Members', readonly=True)
    jobs_ids = fields.One2many('project.offer', 'department_id', 'Projets')"""


    def name_get(self, cr, uid, ids, conText=None):
        if conText is None:
            conText = {}
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], conText=conText)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
    


class ProjectCandidate(models.Model):

    """hr.employee"""
    _inherits = {"res.users": 'user_id'}
    _name = 'project.candidate'

    submission_ids = fields.One2many('project.submission', 'candidate', 'Candidatures')
    user_id = fields.Many2one('res.users', 'Utilisateur lié', track_visibility='onchange')
    
    _mail_post_access = 'read'

    name_Related = fields.Related('resource_id', 'name', type='Char', string='Name', readonly=True, store=True)
    
    def _get_image(self, cr, uid, ids, name, args, conText=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, conText=conText):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, conText=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, conText=conText)

    
    
    birthday = fields.Datetime('Date de naisssance"', readonly=False, select=True)
    ssnid = fields.Char('SSN No', help='Social Security Number')
    sinid = fields.Char('SIN No', help="Social Insurance Number")
    identification_id = fields.Char('Identification No')
    otherid = fields.Char('Other Id')
    gender = fields.selection([('male', 'Male'), ('female', 'Female')], 'Gender')
    marital = fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status')
    department_id = fields.Many2one('hr.department', 'Department')
    address_id = fields.Many2one('res.partner', 'Working Address')
    address_home_id = fields.Many2one('res.partner', 'Home Address')
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Account Number', domain="[('partner_id','=',address_home_id)]", help="Employee bank salary account")
    work_phone = fields.Char('Work Phone', readonly=False)
    mobile_phone = fields.Char('Work Mobile', readonly=False)
    work_email = fields.Char('Work Email', size=240)
    work_location = fields.Char('Office Location')
    notes = fields.Text('Notes')
    parent_id = fields.Many2one('project.candidate', 'Candidat')
    category_ids = fields.many2many('project.candidate.category', 'Candidat_category_rel', 'Cand_id', 'category_id', 'Tags')
    child_ids = fields.One2many('project.candidate', 'parent_id', 'Subordinates'),
    resource_id = fields.Many2one('resource.resource', 'Resource', ondelete='cascade', required=True, auto_join=True),
    """coach_id = fields.Many2one('project.candidate', 'Coach')"""
    job_id = fields.Many2one('project.offer', 'Offer Title')
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.binary("Photo",
       help="This field holds the image used as photo for the employee, limited to 1024x1024px."),
    image_medium = fields.Function(_get_image, fnct_inv=_set_image,
        string="Medium-sized photo", type="binary", multi="_get_image",
        store = {
            'project.candidate': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
        },
        help="Medium-sized photo of the employee. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small = fields.Function(_get_image, fnct_inv=_set_image,
        string="Small-sized photo", type="binary", multi="_get_image",
        store = {
            'project.candidate': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
        },
        help="Small-sized photo of the employee. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")
    passport_id = fields.Char('Passport No')
    color = fields.Integer('Color Index')
    city = fields.Related('address_id', 'city', type='Char', string='City')
    login = fields.Related('user_id', 'login', type='Char', string='Login', readonly=1)
    last_login = fields.Related('user_id', 'date', type='Datetime', string='Latest Connection', readonly=1)
    
    def _get_default_image(self, cr, uid, conText=None):
        image_path = get_module_resource('project', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    defaults = {
        'active': 1,
        'image': _get_default_image,
        'color': 0,
    }
    
    
    def create(self, cr, uid, data, conText=None):
        conText = dict(conText or {})
        if conText.get("mail_broadcast"):
            conText['mail_create_nolog'] = True

        Candidate_id = super(ProjectCandidate, self).create(cr, uid, data, conText=conText)

        if conText.get("mail_broadcast"):
            self._broadcast_welcome(cr, uid, Candidate_id, conText=conText)
        return Candidate_id

    def unlink(self, cr, uid, ids, conText=None):
        resource_ids = []
        for candidate in self.browse(cr, uid, ids, conText=conText):
            resource_ids.append(candidate.resource_id.id)
        super(ProjectCandidate, self).unlink(cr, uid, ids, conText=conText)
        return self.pool.get('resource.resource').unlink(cr, uid, resource_ids, conText=conText)

    def onchange_address_id(self, cr, uid, ids, address, conText=None):
        if address:
            address = self.pool.get('res.partner').browse(cr, uid, address, conText=conText)
            return {'value': {'work_phone': address.phone, 'mobile_phone': address.mobile}}
        return {'value': {}}
    
    def onchange_company(self, cr, uid, ids, company, conText=None):
        address_id = False
        if company:
            company_id = self.pool.get('res.company').browse(cr, uid, company, conText=conText)
            address = self.pool.get('res.partner').address_get(cr, uid, [company_id.partner_id.id], ['default'])
            address_id = address and address['default'] or False
        return {'value': {'address_id': address_id}}

    def onchange_TypeProjet_id(self, cr, uid, ids, type_id, conText=None):
        value = {'parent_id': False}
        if type_id:
            type = self.pool.get('project.type').browse(cr, uid, type_id)
            value['parent_id'] = type.manager_id.id
        return {'value': value}

    def onchange_user(self, cr, uid, ids, user_id, conText=None):
        work_email = False
        if user_id:
            work_email = self.pool.get('res.users').browse(cr, uid, user_id, conText=conText).email
        return {'value': {'work_email': work_email}}
    
    
    
class ProjectRequest(models.Model):  
    
    """hr.employee"""
    _inherits = {"res.users": 'user_id'}
    _name = 'project.request'
    
    name = fields.Char(string='Objet', size=200)
    
    type_id = fields.Many2one('project.request.type', 'Type de demande')
    
    projet_id = fields.Many2one('project.submission', 'Projet')
    
    date_demande = fields.Datetime('Demande', readonly=True, select=True)
    date_aprobation = fields.Datetime('Demande', readonly=True, select=True)
    
    def _get_attached_docs(self, cr, uid, ids, field_name, arg, conText=None):
        res = {}
        attachment_obj = self.pool.get('ir.attachment')
        for offer_id in ids:
            submission_ids = self.pool.get('project.submission').search(cr, uid, [('offer_id', '=', offer_id)], conText=conText)
            res[offer_id] = attachment_obj.search(
                cr, uid, [
                    '|',
                    '&', ('res_model', '=', 'project.offer'), ('res_id', '=', offer_id),
                    '&', ('res_model', '=', 'project.submission'), ('res_id', 'in', submission_ids)
                ], conText=conText)
        return res
    
    def _count_all(self, cr, uid, ids, field_name, arg, conText=None):
        Submission = self.pool['project.submission']
        return {
            offer_id: {
                'submission_count': Submission.search_count(cr,uid, [('offer_id', '=', offer_id)], conText=conText),
                'documents_count': len(self._get_attached_docs(cr, uid, [offer_id], field_name, arg, conText=conText)[offer_id])
            }
            for offer_id in ids
        }

    
    etat = fields.Selection(REQSOUMISS_ETAT, 'Submission')
    document_ids =  fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents')
    documents_count =  fields.Function(_count_all, type='Integer', string='Documents', multi=True)
    
    
    