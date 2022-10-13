from odoo import models, fields, api

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    operation_template_id = fields.Many2one('mrp.routing.workcenter.template', related='operation_id.operation_template_id', store=True, readonly=True)