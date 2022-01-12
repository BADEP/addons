# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    purchase_ids = fields.One2many(
        'purchase.order',
        'project_id',
        string='Achats',
    )
    purchase_open_count = fields.Integer('Nombre d\'achats', compute='_compute_purchase_count')

    @api.depends('purchase_ids')
    def _compute_purchase_count(self):
        for project in self:
            project.purchase_open_count = len(
                project.purchase_ids.filtered(lambda p: p.invoice_status in ('no', 'to invoice') and p.state == 'purchase'))