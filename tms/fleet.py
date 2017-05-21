from openerp import fields, models


class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    driver_id = fields.Many2one('hr.employee', domain=[('is_driver', '=', True)])
    mpg = fields.Float()

fleet_vehicle()
