from odoo import models, fields, api, exceptions, _

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    pickings = fields.One2many('stock.picking', 'vehicle', string='Pickings')
    picking_count = fields.Integer(compute='get_picking_count', store=False)
    picking_ok = fields.Boolean(string='Available in Pickings',default=True)
    stock_location_id = fields.Many2one('stock.location', string='Stock Location')

    @api.one
    @api.depends('pickings')
    def get_picking_count(self):
        self.picking_count = len(self.pickings.filtered(lambda s: s.state != 'cancel'))

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

    # @api.model
    # def create_stock_location(self, name, user=None):
    #     if not user:
    #         user = self.env.user
    #     if not user.warehouse_id:
    #         raise exceptions.Warning(_('Your user has no assigned any '
    #                                    'warehouse, you must assign one.'))
    #     return self.env['stock.location'].create({
    #         'location_id': self.env.user.warehouse_id.lot_stock_id.id,
    #         'usage': 'internal',
    #         'name': name})
    #
    # @api.model
    # def create(self, vals):
    #     #todo: use name instead
    #     if not vals.get('stock_location_id') and vals.get('license_plate'):
    #         loc_id = self.create_stock_location(vals['license_plate'])
    #         vals['stock_location_id'] = loc_id.id
    #     return super(FleetVehicle, self).create(vals)