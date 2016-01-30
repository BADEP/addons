# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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

import copy

from openerp import netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _


class sale_order(osv.osv):
    _inherit = "sale.order"
    _name = "sale.order"
    _columns = {
        'global_discount': fields.float('Discount (%)', digits_compute=dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
    }
    
    def onchange_global_discount(self, cr, uid, ids, global_discount, context):
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                line.discount = global_discount
        return True
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
