from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    routing_id = fields.Many2one(
        'mrp.routing', 'Routing', help="The operations for producing this BoM.  When a routing is specified, the production orders will "
                                       " be executed through work orders, otherwise everything is processed in the production order itself. ")

    @api.onchange('routing_id')
    def onchange_routing_id(self):
        for line in self.bom_line_ids:
            line.operation_id = False
        self.operation_ids.unlink()
        if self.routing_id:
            self.operation_ids = [(0, 0, {
                'name': x.name,
                'sequence': x.sequence,
                'workcenter_id': x.workcenter_id.id,
                'operation_template_id': x.id,
                'company_id': x.company_id,
                'worksheet_type': x.worksheet_type,
                'note': x.note,
                'worksheet': x.worksheet,
                'worksheet_google_slide': x.worksheet_google_slide,
                'time_mode': x.time_mode,
                'time_mode_batch': x.time_mode_batch,
                'time_cycle_manual': x.time_cycle_manual
            }) for x in self.routing_id.operation_ids]


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    routing_id = fields.Many2one(
        'mrp.routing', 'Routing',
        related='bom_id.routing_id', store=True, readonly=False,
        help="The list of operations to produce the finished product. The routing is mainly used to "
             "compute work center costs during operations and to plan future loads on work centers "
             "based on production planning.")
