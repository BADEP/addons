# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    vehicle = fields.Many2one('fleet.vehicle', domain=[('purchase_ok','=',True)], readonly=True, states={'draft': [('readonly', False)]})
    driver = fields.Many2one('res.partner', readonly=True, states={'draft': [('readonly', False)]})
    
    @api.onchange('vehicle')
    def set_driver(self):
        if self.vehicle and self.vehicle.driver_id:
            self.driver = self.vehicle.driver_id
        else:
            self.driver = False

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        res.update({
            'vehicle': self.vehicle.id,
            'driver': self.driver.id
        })
        return res