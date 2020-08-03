import logging
import requests

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class CrmFacebookPage(models.Model):
    _name = 'crm.facebook.page'
    _description = 'Facebook Page'

    label = fields.Char(string='Page Label')
    # TODO: rename to id
    name = fields.Char(required=True, string='Page ID')
    access_token = fields.Char(required=True, string='Page Access Token')
    form_ids = fields.One2many('crm.facebook.form', 'page_id', string='Lead Forms')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'You cannot create a Page twice')
    ]

    @api.depends('label', 'name')
    def name_get(self):
        result = []
        for page in self:
            name = page.label if page.label else page.name
            result.append((page.id, name))
        return result

    def form_processing(self, r):
        if not r.get('data'):
            return
        for form in r['data']:
            if self.form_ids.filtered(
                    lambda f: f.facebook_form_id == form['id']):
                continue
            if form['status'] == 'ACTIVE':
                self.env['crm.facebook.form'].create({
                    'name': form['name'],
                    'facebook_form_id': form['id'],
                    'page_id': self.id}).get_fields()

        if r.get('paging') and r['paging'].get('next'):
            self.form_processing(requests.get(r['paging']['next']).json())
        return

    def get_forms(self):
        r = requests.get("https://graph.facebook.com/v7.0/" + self.name + "/leadgen_forms",
                         params={'access_token': self.access_token}).json()
        if r.get('error'):
            raise ValidationError(r['error']['message'])
        self.form_processing(r)

class CrmFacebookForm(models.Model):
    _name = 'crm.facebook.form'
    _description = 'Facebook Form Page'

    name = fields.Char(required=True)
    facebook_form_id = fields.Char(required=True, string='Form ID')
    access_token = fields.Char(required=True, related='page_id.access_token', string='Page Access Token')
    page_id = fields.Many2one('crm.facebook.page', readonly=True, ondelete='cascade', string='Facebook Page')
    mappings = fields.One2many('crm.facebook.form.field', 'form_id')
    team_id = fields.Many2one('crm.team', domain=['|', ('use_leads', '=', True), ('use_opportunities', '=', True)],
                              string="Sales Team")
    campaign_id = fields.Many2one('utm.campaign')
    source_id = fields.Many2one('utm.source')
    medium_id = fields.Many2one('utm.medium')

    def get_fields(self):
        self.mappings.unlink()
        r = requests.get("https://graph.facebook.com/v7.0/" + self.facebook_form_id,
                         params={'access_token': self.access_token, 'fields': 'questions'}).json()
        if r.get('error'):
            raise ValidationError(r['error']['message'])
        if r.get('questions'):
            for question in r.get('questions'):
                self.env['crm.facebook.form.field'].create({
                    'form_id': self.id,
                    'name': question['label'],
                    'facebook_field': question['key'],
                    'odoo_field': self.env['crm.facebook.form.mapping'].search(
                        [('facebook_field', '=', question['key'])], limit=1) and self.env[
                                      'crm.facebook.form.mapping'].search([('facebook_field', '=', question['key'])],
                                                                          limit=1).odoo_field.id or ''
                })

    def action_guess_mapping(self):
        for rec in self:
            rec.mappings.action_guess_mapping()

class CrmFacebookFormField(models.Model):
    _name = 'crm.facebook.form.field'
    _description = 'Facebook form fields'

    form_id = fields.Many2one('crm.facebook.form', required=True, ondelete='cascade', string='Form')
    name = fields.Char()
    odoo_field = fields.Many2one('ir.model.fields',
                                 domain=[('model', '=', 'crm.lead'),
                                         ('store', '=', True),
                                         ('ttype', 'in', ('char',
                                                          'date',
                                                          'datetime',
                                                          'float',
                                                          'html',
                                                          'integer',
                                                          'monetary',
                                                          'many2one',
                                                          'selection',
                                                          'phone',
                                                          'text'))],
                                 required=False)
    facebook_field = fields.Char(required=True)

    def action_guess_mapping(self):
        for rec in self:
            mapping = self.env['crm.facebook.form.mapping'].search([('facebook_field', '=', rec.facebook_field)],
                                                                   limit=1)
            if mapping:
                rec.odoo_field = mapping.odoo_field

    _sql_constraints = [
        ('field_unique', 'unique(form_id, odoo_field, facebook_field)', 'Mapping must be unique per form')
    ]


class CrmFacebookFormMapping(models.Model):
    _name = 'crm.facebook.form.mapping'
    _description = 'Default field mapping for new forms'

    odoo_field = fields.Many2one('ir.model.fields',
                                 domain=[('model', '=', 'crm.lead'),
                                         ('store', '=', True),
                                         ('ttype', 'in', ('char',
                                                          'date',
                                                          'datetime',
                                                          'float',
                                                          'html',
                                                          'integer',
                                                          'monetary',
                                                          'many2one',
                                                          'selection',
                                                          'phone',
                                                          'text'))],
                                 required=True)
    facebook_field = fields.Char(required=True)

    _sql_constraints = [
        ('map_unique', 'unique(odoo_field, facebook_field)', 'Default Mapping must be unique')
    ]
