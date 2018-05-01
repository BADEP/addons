# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    pickings = fields.One2many('stock.picking', 'vehicle', string='Pickings')
    picking_count = fields.Integer(compute='get_picking_count', store=False)
    picking_ok = fields.Boolean(string='Available in Pickings',default=True)

    @api.one
    @api.depends('pickings')
    def get_picking_count(self):
        self.picking_count = len(self.pickings.filtered(lambda s: s.state != 'cancel'))

    @api.multi
    def act_show_pickings(self):
        action = self.env.ref('stock.action_picking_tree_all')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        result['domain'] = "[('id','in',["+','.join(map(str, self.pickings.ids))+"])]"
        return result