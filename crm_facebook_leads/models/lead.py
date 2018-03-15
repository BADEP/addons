# -*- coding: utf-8 -*-

from odoo import models, fields, api

import requests
import re, time


class CrmFacebookForm(models.Model):
    _name = 'crm.facebook.form'
    
    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    facebook_form_id = fields.Char(required=True, string='Form ID')
    access_token = fields.Char(required=True)
    mappings = fields.One2many('crm.facebook.form.field', 'form_id')
    team_id = fields.Many2one('crm.team', domain=['|', ('use_leads', '=', True), ('use_opportunities', '=', True)], string="Assign Team")
    
class CrmFacebookFormField(models.Model):
    _name = 'crm.facebook.form.field'

    form_id = fields.Many2one('crm.facebook.form', required=True)
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
                        ('field_unique', 'unique(form_id, odoo_field, facebook_field)', 'Mapping must be unique per form')
    ]
    
class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    facebook_lead_id = fields.Char()
    
    _sql_constraints = [
                        ('facebook_lead_unique', 'unique(facebook_lead_id)', 'This Facebook lead already exists!')
    ]
    
    @api.model
    def get_facebook_leads(self):
        forms = self.env['crm.facebook.form'].search([('active', '=', True)])
        for form in forms:
            r = requests.get("https://graph.facebook.com/v2.12/" + form.facebook_form_id + "/leads", params = {'access_token': form.access_token})
            response = r.json()
            if response['data']:
                for lead in response['data']:
                    if not self.search([('facebook_lead_id', '=', lead.get('id')), ('active', 'in', (True, False))]):
                        vals = {}
                        notes = []
                        for field_data in lead['field_data']:
                            if field_data['name'] in form.mappings.mapped('facebook_field'):
                                odoo_field = form.mappings.filtered(lambda m: m.facebook_field == field_data['name']).odoo_field
                                if odoo_field.ttype == 'many2one':
                                    related_value = self.env[odoo_field.relation].search([('display_name', '=', field_data['values'][0])])
                                    vals.update({odoo_field.name: related_value and related_value.id})
                                elif odoo_field.ttype in ('float', 'monetary'):
                                    vals.update({odoo_field.name: float(field_data['values'][0])})
                                elif odoo_field.ttype == 'integer':
                                    vals.update({odoo_field.name: int(field_data['values'][0])})
                                elif odoo_field.ttype in ('date', 'datetime', 'selection'):
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
                            'date_open': lead['created_time'].split('+')[0].replace('T', ' ')
                        })
                        lead = self.create(vals)
                    
        