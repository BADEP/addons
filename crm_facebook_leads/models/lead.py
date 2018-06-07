# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests

class CrmFacebookPage(models.Model):
    _name = 'crm.facebook.page'
    
    name = fields.Char(required=True)
    access_token = fields.Char(required=True, string='Page Access Token')
    form_ids = fields.One2many('crm.facebook.form', 'page_id', string='Lead Forms')
    
    @api.multi
    def get_forms(self):
        r = requests.get("https://graph.facebook.com/v2.12/" + self.name + "/leadgen_forms", params = {'access_token': self.access_token}).json()
        for form in r['data']:
            if not self.form_ids.filtered(lambda f: f.facebook_form_id == form['id']):
                self.env['crm.facebook.form'].create({
                                                'name': form['name'],
                                                'facebook_form_id': form['id'],
                                                'page_id': self.id
                                             }).get_fields()

class CrmFacebookForm(models.Model):
    _name = 'crm.facebook.form'
    
    name = fields.Char(required=True)
    facebook_form_id = fields.Char(required=True, string='Form ID')
    access_token = fields.Char(required=True, related='page_id.access_token', string='Page Access Token')
    page_id = fields.Many2one('crm.facebook.page', readonly=True, ondelete='cascade', string='Facebook Page')
    mappings = fields.One2many('crm.facebook.form.field', 'form_id')
    team_id = fields.Many2one('crm.team', domain=['|', ('use_leads', '=', True), ('use_opportunities', '=', True)], string="Sales Team")
    campaign_id = fields.Many2one('utm.campaign', string='Campaign')
    source_id = fields.Many2one('utm.source', string='Source')
    medium_id = fields.Many2one('utm.medium', string='Medium')
    
    def get_fields(self):
        self.mappings.unlink()
        r = requests.get("https://graph.facebook.com/v2.12/" + self.facebook_form_id, params = {'access_token': self.access_token, 'fields': 'qualifiers'}).json()
        if r.get('qualifiers'):
            for qualifier in r.get('qualifiers'):
                self.env['crm.facebook.form.field'].create({
                                                                'form_id': self.id,
                                                                'name': qualifier['label'],
                                                                'facebook_field': qualifier['field_key']
                                                            })

class CrmFacebookFormField(models.Model):
    _name = 'crm.facebook.form.field'

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
    
    _sql_constraints = [
                        ('field_unique', 'unique(form_id, odoo_field, facebook_field)', 'Mapping must be unique per form')
    ]
class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    facebook_lead_id = fields.Char('Lead ID')
    facebook_page_id = fields.Many2one('crm.facebook.page', related='facebook_form_id.page_id', store=True, string='Page', readonly=True)
    facebook_form_id = fields.Many2one('crm.facebook.form', string='Form')
    
    _sql_constraints = [
                        ('facebook_lead_unique', 'unique(facebook_lead_id)', 'This Facebook lead already exists!')
    ]
    
    @api.model
    def get_facebook_leads(self):
        for page in self.env['crm.facebook.page'].search([]):
            forms = self.env['crm.facebook.form'].search([('page_id', '=', page.id)])
            for form in forms:
                r = requests.get("https://graph.facebook.com/v2.12/" + form.facebook_form_id + "/leads", params = {'access_token': form.access_token}).json()
                if r.get('data'):
                    for lead in r['data']:
                        if not self.search([('facebook_lead_id', '=', lead.get('id')), '|', ('active', '=', True), ('active', '=', False)]):
                            vals = {}
                            notes = []
                            for field_data in lead['field_data']:
                                if field_data['name'] in form.mappings.filtered(lambda m: m.odoo_field.id != False).mapped('facebook_field'):
                                    odoo_field = form.mappings.filtered(lambda m: m.facebook_field == field_data['name']).odoo_field
                                    if odoo_field.ttype == 'many2one':
                                        related_value = self.env[odoo_field.relation].search([('display_name', '=', field_data['values'][0])])
                                        vals.update({odoo_field.name: related_value and related_value.id})
                                    elif odoo_field.ttype in ('float', 'monetary'):
                                        vals.update({odoo_field.name: float(field_data['values'][0])})
                                    elif odoo_field.ttype == 'integer':
                                        vals.update({odoo_field.name: int(field_data['values'][0])})
                                    elif odoo_field.ttype in ('date', 'datetime'):
                                        vals.update({odoo_field.name: field_data['values'][0].split('+')[0].replace('T', ' ')})
                                    elif odoo_field.ttype == 'selection':
                                        vals.update({odoo_field.name: field_data['values'][0]})
                                    else:
                                        vals.update({odoo_field.name: ", ".join(field_data['values'])})
                                else:
                                    notes.append(field_data['name'] + ": " + ", ".join(field_data['values']))
                            if not vals.get('name'):
                                vals.update({'name': form.name + " - " + lead['id']})
                            vals.update({
                                'facebook_lead_id': lead['id'],
                                'description': "\n".join(notes),
                                'team_id': form.team_id and form.team_id.id,
                                'campaign_id': form.campaign_id and form.campaign_id.id,
                                'source_id': form.source_id and form.source_id.id,
                                'medium_id': form.medium_id and form.medium_id.id,
                                'facebook_form_id': form.id,
                                'date_open': lead['created_time'].split('+')[0].replace('T', ' ')
                            })
                            lead = self.create(vals)
