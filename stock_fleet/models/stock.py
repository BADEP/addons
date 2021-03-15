# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    vehicle = fields.Many2one('fleet.vehicle', domain=[('picking_ok','=',True)])
    driver = fields.Many2one('res.partner')
    odometer = fields.Float('Kilométrage', related='vehicle.odometer', store=True, readonly=False)
    
    @api.onchange('vehicle')
    def set_driver(self):
        if self.vehicle and self.vehicle.driver_id:
            self.driver = self.vehicle.driver_id
        else:
            self.driver = False
        #todo: initialise picking location on vehicle location
        if self.vehicle and self.vehicle.stock_location_id:
            pass

class StockMove(models.Model):
    _inherit = 'stock.move'
    vehicle = fields.Many2one('fleet.vehicle', related='picking_id.vehicle', store=True, readonly=True)
    driver = fields.Many2one('res.partner', related='picking_id.driver', store=True, readolny=True)
    odometer = fields.Float('Kilométrage', related='picking_id.odometer', store=True, readolny=True)
