# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 BADEP. All Rights Reserved.
#    Author: Khalid Hazam<k.hazam@badep.ma>
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from openerp.osv import osv, fields as oldfields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    sale_orders = fields.One2many('sale.order', 'vehicle')
    sales_count = fields.Float(digits_compute=dp.get_precision('Account'), compute='get_sales_count')
    stock_pickings = fields.One2many('stock.picking', 'vehicle')
    pickings_count = fields.Float(digits_compute=dp.get_precision('Account'), compute='get_pickings_count')
    partner_id = fields.Many2one('res.partner', string="Propriétaire")
    name = fields.Char(compute='get_name')
    is_company_owned = fields.Boolean(string='Appartient à la société', compute='get_is_company_owned',store=True)
    sale_ok = fields.Boolean(string='Disponible dans les ventes',default=True)
    purchase_ok = fields.Boolean(string='Disponible dans les achats',default=True)
    
    @api.one
    @api.depends('partner_id')
    def get_is_company_owned(self):
        if self.partner_id and self.partner_id.id == self.env.user.company_id.partner_id.id:
            self.is_company_owned = True
        else:
            self.is_company_owned = False
    @api.one
    @api.depends('partner_id','license_plate')
    def get_name(self):
        if self.partner_id:
            self.name = self.partner_id.display_name + ' / ' + self.license_plate
        else:
            self.name = self.model_id.brand_id.name + '/' + self.model_id.modelname + ' / ' + self.license_plate

    @api.one
    @api.depends('sale_orders')
    def get_sales_count(self):
        total = 0
        for order in self.sale_orders:
            if order.state in ('progress', 'done', 'manual'):
                total += order.amount_total
        self.sales_count = total
    
    @api.one
    @api.depends('stock_pickings')
    def get_pickings_count(self):
        self.pickings_count = len(self.stock_pickings)

    @api.multi
    def act_show_sales(self):
        action = self.env.ref('sale.action_orders')

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
        result['domain'] = "[('id','in',["+','.join(map(str, self.sale_orders.ids))+"])]"
        return result
    
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
        result['domain'] = "[('id','in',["+','.join(map(str, self.stock_pickings.ids))+"])]"
        return result