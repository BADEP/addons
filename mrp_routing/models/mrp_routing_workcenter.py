from odoo import models, fields, api

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    operation_template_id = fields.Many2one('mrp.routing.workcenter.template', string='Operation Template', readonly=True, store=True)