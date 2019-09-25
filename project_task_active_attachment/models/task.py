# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def write(self, vals):
        res = super(ProjectTask, self).write(vals) if vals else True
        if 'active' in vals:
            self.with_context(active_test=False).env['ir.attachment'].search([('res_model', '=', self._name), ('res_id', '=', self.ids)]).write({'active': vals['active']})
        return res
