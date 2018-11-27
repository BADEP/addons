# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    vehicle = fields.Many2one('fleet.vehicle', domain=[('sale_ok','=',True)], readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    driver = fields.Many2one('res.partner', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.onchange('vehicle')
    def set_driver(self):
        if self.vehicle and self.vehicle.driver_id:
            self.driver = self.vehicle.driver_id
        else:
            self.driver = False

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.picking_ids.write({'vehicle': self.vehicle and self.vehicle.id, 'driver': self.driver and self.driver.id})
        return res
