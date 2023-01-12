# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    purchase_request_ids = fields.One2many(
        'purchase.request',
        'project_id',
        string='Demandes d\'achat',
    )
    purchase_request_count = fields.Integer('Nombre de DA', compute='_compute_purchase_request_count')

    @api.depends('purchase_request_ids')
    def _compute_purchase_request_count(self):
        for project in self:
            project.purchase_request_count = len(project.purchase_request_ids)