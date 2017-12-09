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

from openerp.osv import osv


class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def action_recompute(self, cr, uid, ids, context=None):
        context = context or {}
        for order in self.browse(cr, uid, ids, context=context):
            pricelist_id = order.pricelist_id.id
            if not pricelist_id:
                return {}
            for line in order.order_line:
                price = self.pool.get('product.pricelist').price_get(cr, uid, pricelist_id,
                                                                     line.product_id.id, line.product_uos_qty or 1.0, order.partner_id.id, {
                                                                                                       'uom': line.product_uom.id,
                                                                                                       'date': order.date_order,
                                                                                                       })
                line.price_unit = price.items()[0][1]
        return True
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
