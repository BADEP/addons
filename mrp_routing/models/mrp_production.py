from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    routing_id = fields.Many2one('mrp.routing', related='bom_id.routing_id', readonly=True)