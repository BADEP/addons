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

from openerp.osv import osv
from openerp.tools.translate import _


class pos_order(osv.osv):
    _inherit = "pos.order"
    _name = "pos.order"
    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')

        for order in self.browse(cr, uid, ids, context=context):
            addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
            picking_type = order.picking_type_id
            picking_id = False
            if picking_type:
                picking_id = picking_obj.create(cr, uid, {
                    'origin': order.name,
                    'partner_id': addr.get('delivery', False),
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'invoice_state': 'none',
                }, context=context)
                self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            elif picking_type:
                if not picking_type.default_location_dest_id:
                    raise osv.except_osv(_('Error!'), _('Missing source or destination location for picking type %s. Please configure those fields and try again.' % (picking_type.name,)))
                destination_id = picking_type.default_location_dest_id.id
            else:
                destination_id = partner_obj.default_get(cr, uid, ['property_stock_customer'], context=context)['property_stock_customer']

            move_list = []
            for line in order.lines:
                if line.product_id and line.product_id.type == 'service':
                    continue
                if line.product_id.bundle == True:
                    for item in line.product_id.item_ids:
                        move_list.append(move_obj.create(cr, uid, {
                            'picking_id': picking_id,
                            'picking_type_id': picking_type.id,
                            'state': 'draft',
                            'location_id': location_id if line.qty >= 0 else destination_id,
                            'location_dest_id': destination_id if line.qty >= 0 else location_id,
                            'name': item.item_id.name,
                            'product_id': item.item_id.id,
                            'product_uom_qty': abs(line.qty * item.qty_uom),
                            'product_uom': item.uom_id.id,
                            'product_uos_qty': abs(line.qty * item.qty_uom),
                            'product_uos': item.uom_id.id,
                        }, context=context))
                else:
                    move_list.append(move_obj.create(cr, uid, {
                        'name': line.name,
                        'product_uom': line.product_id.uom_id.id,
                        'product_uos': line.product_id.uom_id.id,
                        'picking_id': picking_id,
                        'picking_type_id': picking_type.id,
                        'product_id': line.product_id.id,
                        'product_uos_qty': abs(line.qty),
                        'product_uom_qty': abs(line.qty),
                        'state': 'draft',
                        'location_id': location_id if line.qty >= 0 else destination_id,
                        'location_dest_id': destination_id if line.qty >= 0 else location_id,
                    }, context=context))
            if picking_id:
                picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                # picking_obj.force_assign(cr, uid, [picking_id], context=context)
                # picking_obj.action_done(cr, uid, [picking_id], context=context)
            elif move_list:
                move_obj.action_confirm(cr, uid, move_list, context=context)
                # move_obj.force_assign(cr, uid, move_list, context=context)
                # move_obj.action_done(cr, uid, move_list, context=context)
        return True
pos_order()

class sale_order(osv.osv):
    _inherit = "sale.order"
    _name = "sale.order"

    def _prepare_order_line_procurement(self, cr, uid, order, line, item=False, group_id=False, context=None):
        vals = []
        if item == False:
            if line.product_id.bundle == True:
                for item in line.product_id.item_ids:
                    return_vals = self._prepare_order_line_procurement(cr, uid, order, line, item, group_id, context)
                    for return_val in return_vals:
                        vals.append(return_val)
            else:
                date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)
                val = {
                    'name': line.name,
                    'origin': order.name,
                    'date_planned': date_planned,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
                    'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
                    'company_id': order.company_id.id,
                    'group_id': group_id,
                    'invoice_state': (order.order_policy == 'picking') and '2binvoiced' or 'none',
                    'sale_line_id': line.id,
                    'location_id' : order.partner_shipping_id.property_stock_customer.id,
                    'route_ids' : line.route_id and [(4, line.route_id.id)] or [],
                    'warehouse_id' : order.warehouse_id and order.warehouse_id.id or False,
                    'partner_dest_id' : order.partner_shipping_id.id
                }
                vals.append(val)
        else:
            if item.item_id.bundle == True:
                for child_item in item.item_id.item_ids:
                    return_vals = self._prepare_order_line_procurement(cr, uid, order, line, child_item, group_id, context)
                    for return_val in return_vals:
                        vals.append(return_val)
            else:
                date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)
                val = {
                    'name': item.item_id.name,
                    'origin': order.name,
                    'date_planned': date_planned,
                    'product_id': item.item_id.id,
                    'product_qty': line.product_uom_qty * item.qty_uom,
                    'product_uom': line.product_uom.id,
                    'product_uos_qty': line.product_uom_qty * item.qty_uom,
                    'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
                    'company_id': order.company_id.id,
                    'group_id': group_id,
                    'invoice_state': (order.order_policy == 'picking') and '2binvoiced' or 'none',
                    'sale_line_id': line.id,
                    'location_id' : order.partner_shipping_id.property_stock_customer.id,
                    'route_ids' : line.route_id and [(4, line.route_id.id)] or [],
                    'warehouse_id' : order.warehouse_id and order.warehouse_id.id or False,
                    'partner_dest_id' : order.partner_shipping_id.id
                }
                vals.append(val)
        return vals
    
    def action_ship_create(self, cr, uid, ids, context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        :return: True
        """
        procurement_obj = self.pool.get('procurement.order')
        sale_line_obj = self.pool.get('sale.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            proc_ids = []
            vals = self._prepare_procurement_group(cr, uid, order, context=context)
            if not order.procurement_group_id:
                group_id = self.pool.get("procurement.group").create(cr, uid, vals, context=context)
                order.write({'procurement_group_id': group_id})

            for line in order.order_line:
                # Try to fix exception procurement (possible when after a shipping exception the user choose to recreate)
                if line.procurement_ids:
                    # first check them to see if they are in exception or not (one of the related moves is cancelled)
                    procurement_obj.check(cr, uid, [x.id for x in line.procurement_ids if x.state not in ['cancel', 'done']])
                    line.refresh()
                    # run again procurement that are in exception in order to trigger another move
                    proc_ids += [x.id for x in line.procurement_ids if x.state in ('exception', 'cancel')]
                    procurement_obj.reset_to_confirmed(cr, uid, proc_ids, context=context)
                elif sale_line_obj.need_procurement(cr, uid, [line.id], context=context):
                    if (line.state == 'done') or not line.product_id:
                        continue
                    for val in self._prepare_order_line_procurement(cr, uid, order, line, group_id=order.procurement_group_id.id, context=context):
                        proc_id = procurement_obj.create(cr, uid, val, context=context)
                        proc_ids.append(proc_id)
            # Confirm procurement order such that rules will be applied on it
            # note that the workflow normally ensure proc_ids isn't an empty list
            procurement_obj.run(cr, uid, proc_ids, context=context)

            # if shipping was in exception and the user choose to recreate the delivery order, write the new status of SO
            if order.state == 'shipping_except':
                val = {'state': 'progress', 'shipped': False}

                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
                order.write(val)
        return True
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
