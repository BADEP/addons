# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 OpenERP S.A (<http://www.openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from datetime import timedelta

class sale_order(models.Model):
    _inherit = 'sale.order'

    date_start = fields.Datetime(string='Date Start', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now())
    date_end = fields.Datetime('Date End', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'log_progress': [('readonly', False)]}, copy=False)
    vehicle = fields.Many2one('fleet.vehicle', string='Véhicule', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    driver = fields.Many2one('hr.employee', related='vehicle.driver_id', store = True, readonly=True)
    fuel_log = fields.Many2one('fleet.vehicle.log.fuel', string='Bon de carburant', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},)
    estimated_fuel_qty = fields.Float(compute='get_fuel_qty')
    state = fields.Selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('log_progress', 'En cours de livraison'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True)
        
    @api.one
    @api.depends('order_line')
    def get_fuel_qty(self):
        qty = 0
        for line in self.order_line:
            qty += line.estimated_fuel_qty
        self.estimated_fuel_qty = qty

    @api.one
    @api.onchange('order_line', 'date_start')
    def onchange_set_date_end(self):
        date_end = fields.Datetime.from_string(self.date_start)
        for line in self.order_line:
            if line.partner_picking_id and line.partner_delivery_id:
                grid = self.env['transport.grid'].search([('city_from','=',line.partner_picking_id.city.id), ('city_to','=', line.partner_delivery_id.city.id)])
                if grid:
                    date_end += timedelta(hours=grid.time)
        self.date_end = date_end

sale_order()

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    partner_picking_id = fields.Many2one('res.partner', string='Adresse de chargement', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    partner_delivery_id = fields.Many2one('res.partner', string='Adresse de déchargement', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    city_from = fields.Many2one('res.country.state.city', related='partner_picking_id.city', readonly=True, store=False)
    city_to = fields.Many2one('res.country.state.city', related='partner_delivery_id.city', readonly=True, store=False)
    estimated_fuel_qty = fields.Float(compute='get_fuel_qty')
    cargo = fields.One2many('sale.order.line.cargo', 'order_line')
    
    @api.one
    @api.depends('partner_picking_id','partner_delivery_id')
    def get_fuel_qty(self):
        if self.partner_picking_id and self.partner_delivery_id:
            grid = self.env['transport.grid'].search([('city_from','=',self.partner_picking_id.city.id), ('city_to','=', self.partner_delivery_id.city.id)])
            if grid:
                self.estimated_fuel_qty = grid.distance * self.order_id.vehicle.mpg / 100
    
"""    @api.one
    @api.onchange('partner_picking_id','partner_delivery_id')
    def onchange_addresses(self):
        self.product_id = False"""

sale_order_line()

class sale_order_line_cargo(models.Model):
    _name = 'sale.order.line.cargo'
    
    order_line = fields.Many2one('sale.order.line', required=True, ondelete='cascade')
    product = fields.Many2one('product.product', required=True)
    quantity = fields.Float(digits_compute=dp.get_precision('Product UoS'), required=True)
    uom = fields.Many2one('product.uom', required = True, string="Unité de mesure")
    value = fields.Float(digits_compute= dp.get_precision('Product Price'))

sale_order_line_cargo()