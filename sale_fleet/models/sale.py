# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    vehicle = fields.Many2one('fleet.vehicle', domain=[('sale_ok','=',True)], readonly=True, states={'draft': [('readonly', False)]})
    driver = fields.Many2one('res.partner', readonly=True, states={'draft': [('readonly', False)]})
    
    @api.onchange('vehicle')
    def set_driver(self):
        if self.vehicle and self.vehicle.driver_id:
            self.driver = self.vehicle.driver_id
        else:
            self.driver = False
        
    def _prepare_procurement_group(self):
        res = super(SaleOrder, self)._prepare_procurement_group()
        res.update({'vehicle': self.vehicle and self.vehicle.id, 'driver': self.driver and self.driver.id})
        return res