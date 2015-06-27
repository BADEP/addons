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

from openerp import fields, api, models

class sale_make_log_fuel(models.TransientModel):
    _name = 'sale.make.log.fuel'
    
    quantity = fields.Float(required=True, string='Quantité')
    supplier = fields.Many2one('res.partner', domain=[('supplier','=',True)], string='Fournisseur')
    odometer = fields.Float(string='Kilométrage')
    date = fields.Datetime()
    
    @api.model
    def default_get(self, fields):
        res = super(sale_make_log_fuel, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        assert active_model in ('sale.order'), 'Bad context propagation'
        order = self.env['sale.order'].browse(self.env.context.get(('active_ids'), []))
        if not order or len(order)!=1:
            return res
        res.update({'quantity': order.estimated_fuel_qty, 'date': order.date_start})
        return res
    
    @api.one
    def make_log_fuel(self):
        active_model = self.env.context.get('active_model')
        assert active_model in ('sale.order'), 'Bad context propagation'
        order = self.env['sale.order'].browse(self.env.context.get(('active_ids'), []))
        vals = {
                'vehicle_id': order.vehicle.id,
                'liter': self.quantity,
                'odometer': self.odometer,
                'date': self.date,
                'vendor_id': self.supplier.id,
        }
        log_fuel = order.fuel_log.create(vals)
        order.fuel_log = log_fuel
sale_make_log_fuel()