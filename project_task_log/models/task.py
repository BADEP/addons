# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    log_ids = fields.One2many('project.task.log', 'task_id', string='Logs')

    @api.multi
    def write(self, vals):
        if 'user_id' in vals:
            logs = self.log_ids.filtered(lambda l: l.type == 'user')
            self.env['project.task.log'].create({
                'task_id': self.id,
                'old_user_id': self.user_id.id,
                'user_id': vals['user_id'],
                'stage_id': self.stage_id.id,
                'type': 'user',
                'duration': (fields.Datetime.now() - fields.Datetime.from_string(logs[-1].create_date if logs else self.create_date)).total_seconds()
            })
        if 'stage_id' in vals:
            logs = self.log_ids.filtered(lambda l: l.type == 'stage')
            self.env['project.task.log'].create({
                'task_id': self.id,
                'old_stage_id': self.stage_id.id,
                'user_id': self.user_id.id,
                'stage_id': vals['stage_id'],
                'type': 'stage',
                'duration': (fields.Datetime.now() - fields.Datetime.from_string(logs[-1].create_date if logs else self.create_date)).total_seconds()
            })
        return super(ProjectTask, self).write(vals)

class ProjectTaskLog(models.Model):
    _name = 'project.task.log'

    task_id = fields.Many2one('project.task', required=True, ondelete='cascade')
    old_user_id = fields.Many2one('res.users', string='Old user')
    old_stage_id = fields.Many2one('project.task.type', string='Old stage')
    user_id = fields.Many2one('res.users', string='Current User')
    stage_id = fields.Many2one('project.task.type', string='Current Stage')
    type = fields.Selection([('user', 'User'), ('stage', 'Stage')], required=True)
    duration = fields.Integer(string='Duration')
