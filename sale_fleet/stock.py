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

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    vehicle = fields.Many2one('fleet.vehicle', readonly=False, states={'done': [('readonly', True)]}, string='Véhicule')
    driver = fields.Many2one('res.partner', readonly=False, states={'done': [('readonly', True)]}, string='Chauffeur')
    driver_cost = fields.Float(digits_compute=dp.get_precision('Account'), default=0, string='Coût transport')
    
stock_picking()
