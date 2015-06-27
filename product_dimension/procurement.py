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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class procurement_order(models.Model):
    _inherit = "procurement.order"
    dimensions = fields.One2many('procurement.order.dimension','procurement_order')
    
    @api.one
    def _prepare_mo_vals(self, cr, uid, procurement, context=None):
        res_id = procurement.move_dest_id and procurement.move_dest_id.id or False
        newdate = self._get_date_planned(cr, uid, procurement, context=context)
        bom_obj = self.pool.get('mrp.bom')
        if procurement.bom_id:
            bom_id = procurement.bom_id.id
            routing_id = procurement.bom_id.routing_id.id
        else:
            properties = [x.id for x in procurement.property_ids]
            bom_id = bom_obj._bom_find(cr, uid, product_id=procurement.product_id.id,
                                       properties=properties, context=context)
            bom = bom_obj.browse(cr, uid, bom_id, context=context)
            routing_id = bom.routing_id.id
        return {
            'origin': procurement.origin,
            'product_id': procurement.product_id.id,
            'product_qty': procurement.product_qty,
            'product_uom': procurement.product_uom.id,
            'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
            'product_uos': procurement.product_uos and procurement.product_uos.id or False,
            'location_src_id': procurement.location_id.id,
            'location_dest_id': procurement.location_id.id,
            'bom_id': bom_id,
            'routing_id': routing_id,
            'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
            'move_prod_id': res_id,
            'company_id': procurement.company_id.id,
        }
procurement_order()

class procurement_order_dimension(models.Model):
    _name = "procurement.order.dimension"
    dimension = fields.Many2one('product.uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True)
    procurement_order = fields.Many2one('procurement.order','Procurement Order', required=True, ondelete='cascade')
        
procurement_order_dimension()