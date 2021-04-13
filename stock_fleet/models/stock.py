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
            if self.picking_type_id.code == 'incoming':
                self.location_dest_id = self.vehicle.stock_location_id
                for m in self.move_lines:
                    m.location_dest_id = self.vehicle.stock_location_id
                    for ml in m.move_line_ids:
                        ml.location_dest_id = self.vehicle.stock_location_id
            elif self.picking_type_id.code == 'outgoing':
                self.location_id = self.vehicle.stock_location_id
                for m in self.move_lines:
                    m.location_id = self.vehicle.stock_location_id
                    for ml in m.move_line_ids:
                        ml.location_id = self.vehicle.stock_location_id

    @api.multi
    def write(self, vals):
        if vals.get('vehicle'):
            vehicle = self.env['fleet.vehicle'].browse(vals['vehicle'])
            picking_type_id = self.env['stock.picking.type'].browse(vals['picking_type_id']) if vals.get('picking_type_id') else self.mapped('picking_type_id')
            if vehicle.stock_location_id and picking_type_id:
                if picking_type_id.code == 'incoming':
                    vals.update({'location_dest_id': vehicle.stock_location_id.id})
                elif picking_type_id.code == 'outgoing':
                    vals.update({'location_id': vehicle.stock_location_id.id})
        return super().write(vals)

    @api.model
    def create(self, vals):
        if vals.get('vehicle') and vals.get('picking_type_id'):
            vehicle = self.env['fleet.vehicle'].browse(vals['vehicle'])
            picking_type_id = self.env['stock.picking.type'].browse(vals['picking_type_id'])
            if vehicle.stock_location_id and picking_type_id:
                if picking_type_id.code == 'incoming':
                    vals.update({'location_dest_id': vehicle.stock_location_id.id})
                elif picking_type_id.code == 'outgoing':
                    vals.update({'location_id': vehicle.stock_location_id.id})
        return super().create(vals)

class StockMove(models.Model):
    _inherit = 'stock.move'
    vehicle = fields.Many2one('fleet.vehicle', related='picking_id.vehicle', store=False, readonly=True)
    driver = fields.Many2one('res.partner', related='picking_id.driver', store=False, readolny=True)
    odometer = fields.Float('Kilométrage', related='picking_id.odometer', store=False, readolny=True)

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        res = super()._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        if values.get('force_src_location_id'):
            res.update({'location_id': values['force_src_location_id']})
        return res
