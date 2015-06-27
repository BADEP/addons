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

from openerp.osv import fields,osv
from openerp.tools.float_utils import float_compare

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None, item=False):
        ''' prepare the stock move data from the PO line. This function returns a list of dictionary ready to be used in stock.move's create()'''
        vals = []
        if item == False:
            if order_line.product_id.bundle == True:
                for item in order_line.product_id.item_ids:
                    return_vals = self._prepare_order_line_move(cr, uid, order, order_line, picking_id, group_id, context, item)
                    for return_val in return_vals:
                        vals.append(return_val)
                return vals
            else:
                product_uom = self.pool.get('product.uom')
                price_unit = order_line.price_unit
                if order_line.product_uom.id != order_line.product_id.uom_id.id:
                    price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor
                if order.currency_id.id != order.company_id.currency_id.id:
                    #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
                    price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
                res = []
                move_template = {
                    'name': order_line.name or '',
                    'product_id': order_line.product_id.id,
                    'product_uom': order_line.product_uom.id,
                    'product_uos': order_line.product_uom.id,
                    'date': order.date_order,
                    'date_expected': fields.date.date_to_datetime(self, cr, uid, order_line.date_planned, context),
                    'location_id': order.partner_id.property_stock_supplier.id if order_line.product_qty>0 else order.location_id.id,
                    'location_dest_id': order.location_id.id if order_line.product_qty>0 else order.partner_id.property_stock_supplier.id,
                    'picking_id': picking_id,
                    'partner_id': order.dest_address_id.id or order.partner_id.id,
                    'move_dest_id': False,
                    'state': 'draft',
                    'purchase_line_id': order_line.id,
                    'company_id': order.company_id.id,
                    'price_unit': price_unit,
                    'picking_type_id': order.picking_type_id.id,
                    'group_id': group_id,
                    'procurement_id': False,
                    'origin': order.name,
                    'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
                    'warehouse_id':order.picking_type_id.warehouse_id.id,
                    'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
                }
                if order_line.product_qty>0:
                    diff_quantity = order_line.product_qty
                    for procurement in order_line.procurement_ids:
                        procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=order_line.product_uom.id)
                        tmp = move_template.copy()
                        tmp.update({
                            'product_uom_qty': min(procurement_qty, diff_quantity),
                            'product_uos_qty': min(procurement_qty, diff_quantity),
                            'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
                            'group_id': procurement.group_id.id or group_id,  #move group is same as group of procurements if it exists, otherwise take another group
                            'procurement_id': procurement.id,
                            'invoice_state': procurement.rule_id.invoice_state or (procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state=='2binvoiced' and '2binvoiced') or (order.invoice_method == 'picking' and '2binvoiced') or 'none', #dropship case takes from sale
                            'propagate': procurement.rule_id.propagate,
                        })
                        diff_quantity -= min(procurement_qty, diff_quantity)
                        res.append(tmp)
                    #if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
                    #split the future stock move in two because the route followed may be different.
                    if float_compare(diff_quantity, 0.0, precision_rounding=order_line.product_uom.rounding) > 0:
                        move_template['product_uom_qty'] = diff_quantity
                        move_template['product_uos_qty'] = diff_quantity
                        res.append(move_template)
                else:
                    move_template['product_uom_qty'] = -order_line.product_qty
                    move_template['product_uos_qty'] = -order_line.product_qty
                    res.append(move_template)
                return res
        else:
            if item.item_id.bundle == True:
                for child_item in item.item_id.item_ids:
                    return_vals = self._prepare_order_line_move(cr, uid, order, order_line, picking_id, group_id, context, child_item)
                    for return_val in return_vals:
                        vals.append(return_val)
                return vals
            else:
                product_uom = self.pool.get('product.uom')
                price_unit = order_line.price_unit * (item.revenue/100)
                if order_line.product_uom.id != order_line.product_id.uom_id.id:
                    price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor
                if order.currency_id.id != order.company_id.currency_id.id:
                    #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
                    price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
                res = []
                move_template = {
                    'name': order_line.name + ' (' + item.item_id.name + ')',
                    'product_id': item.item_id.id,
                    'product_uom': order_line.product_uom.id,
                    'product_uos': order_line.product_uom.id,
                    'date': order.date_order,
                    'date_expected': fields.date.date_to_datetime(self, cr, uid, order_line.date_planned, context),
                    'location_id': order.partner_id.property_stock_supplier.id if order_line.product_qty>0 else order.location_id.id,
                    'location_dest_id': order.location_id.id if order_line.product_qty>0 else order.partner_id.property_stock_supplier.id,
                    'picking_id': picking_id,
                    'partner_id': order.dest_address_id.id or order.partner_id.id,
                    'move_dest_id': False,
                    'state': 'draft',
                    'purchase_line_id': order_line.id,
                    'company_id': order.company_id.id,
                    'price_unit': price_unit,
                    'picking_type_id': order.picking_type_id.id,
                    'group_id': group_id,
                    'procurement_id': False,
                    'origin': order.name,
                    'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
                    'warehouse_id':order.picking_type_id.warehouse_id.id,
                    'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
                }
                if order_line.product_qty>0:
                    diff_quantity = order_line.product_qty*item.qty_uom
                    for procurement in order_line.procurement_ids:
                        procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty*item.qty_uom, to_uom_id=order_line.product_uom.id)
                        tmp = move_template.copy()
                        tmp.update({
                            'product_uom_qty': min(procurement_qty, diff_quantity),
                            'product_uos_qty': min(procurement_qty, diff_quantity),
                            'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
                            'group_id': procurement.group_id.id or group_id,  #move group is same as group of procurements if it exists, otherwise take another group
                            'procurement_id': procurement.id,
                            'invoice_state': procurement.rule_id.invoice_state or (procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state=='2binvoiced' and '2binvoiced') or (order.invoice_method == 'picking' and '2binvoiced') or 'none', #dropship case takes from sale
                            'propagate': procurement.rule_id.propagate,
                        })
                        diff_quantity -= min(procurement_qty, diff_quantity)
                        res.append(tmp)
                    #if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
                    #split the future stock move in two because the route followed may be different.
                    if float_compare(diff_quantity, 0.0, precision_rounding=order_line.product_uom.rounding) > 0:
                        move_template['product_uom_qty'] = diff_quantity
                        move_template['product_uos_qty'] = diff_quantity
                        res.append(move_template)
                else:
                    move_template['product_uom_qty'] = -order_line.product_qty
                    move_template['product_uos_qty'] = -order_line.product_qty
                    res.append(move_template)
                return res
                
purchase_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

