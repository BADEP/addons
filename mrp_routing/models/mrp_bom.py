from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, pycompat

from itertools import groupby


class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'
    routing_id = fields.Many2one(
        'mrp.routing', 'Routing',
        track_visibility='onchange',
        help="The operations for producing this BoM.  When a routing is specified, the production orders will "
             " be executed through work orders, otherwise everything is processed in the production order itself. ")

    @api.onchange('routing_id')
    def onchange_routing_id(self):
        for line in self.bom_line_ids:
            line.operation_id = False

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    routing_id = fields.Many2one(
        'mrp.routing', 'Routing',
        related='bom_id.routing_id', store=True, readonly=False,
        help="The list of operations to produce the finished product. The routing is mainly used to "
             "compute work center costs during operations and to plan future loads on work centers "
             "based on production planning.")