# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015-2016 BADEP. All Rights Reserved.
#    Author: Khalid Hazam <k.hazam@badep.ma>
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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from collections import OrderedDict
from openerp.osv import osv
from openerp.tools import float_compare, float_is_zero
from openerp.addons.product import _common
from openerp import tools, SUPERUSER_ID

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    bom_line = fields.Many2one('mrp.bom.line')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
