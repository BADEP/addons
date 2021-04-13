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

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.picking_ids.write({'vehicle': self.vehicle and self.vehicle.id, 'driver': self.driver and self.driver.id})
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self, group_id):
        res = super()._prepare_procurement_values(group_id)
        if self.order_id.vehicle and self.order_id.vehicle.stock_location_id:
            res.update({'force_src_location_id': self.order_id.vehicle.stock_location_id.id})
        return res