from odoo import models, fields, api

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    operation_template_id = fields.Many2one('mrp.routing.workcenter.template', string='Operation Template', readonly=True, store=True)
    routing_id = fields.Many2one('mrp.routing', string='Routing', related='operation_template_id.routing_id', readonly=True, store=True)