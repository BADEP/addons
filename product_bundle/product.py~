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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields


class product_item(osv.osv):
    _name = "product.item"
    _description = "Product Item for Bundle products"
        
    _columns = {
        'sequence':   fields.integer('Sequence'),
        'product_id': fields.many2one('product.product', 'Bundle Product', required=True),
        'item_id':    fields.many2one('product.product', 'Item', required=True),
        'uom_id':     fields.many2one('product.uom', 'UoM', required=True),
        'qty_uom':    fields.integer('Quantity', required=True),
        'revenue':    fields.float('Revenue repartition (%)', help="Define when you sell a Bundle product, how many percent of the sale price is applied to this item."),
        'editable':   fields.boolean('Allow changes in DO ?', help="Allow the user to change this item (quantity or item itself) in the Delivery Orders."),
    }
    _defaults = {
        'editable': lambda *a: True,
    }
    
    
    def onchange_item_id(self, cr, uid, ids, item_id, context=None):
        context = context or {}
        domain = {}
        result = {}
        item = None
        
        if item_id:
            item = self.pool.get('product.template').browse(cr, uid, item_id, context=context)
        
        if item != None:
            result.update({'uom_id': item.uom_id.id})
            domain = {'uom_id': [('category_id', '=', item.uom_id.category_id.id)]}
                
        return {'value': result, 'domain': domain}
    
product_item()

class product_product(osv.osv):
    _inherit = "product.product"

    _columns = {
        'bundle': fields.boolean('Bundle'),
        'item_ids': fields.one2many('product.item', 'product_id', 'Item sets'),
    }
    _defaults = {
        'bundle': False,
    }
product_product()