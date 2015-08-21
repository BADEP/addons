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

class sale_order(models.Model):
    _inherit="sale.order"
    
    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res=super(sale_order,self)._prepare_order_line_procurement(order, line, group_id)
        vals = {
             'dimensions': [(0, 0, {'dimension': d.dimension.id, 'quantity': d.quantity, 'procurement_order': False})  for d in line.dimensions] 
        }
        res.update(vals)
        return res
    
sale_order()

class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    dimensions = fields.One2many('sale.order.line.dimension','sale_order_line', readonly=True, states={'draft': [('readonly', False)]})
    product_visible_qty=fields.Float('Quantity', digits_compute= dp.get_precision('Product UoS'), compute='get_visible_qty')

    @api.depends('dimensions')
    def get_visible_qty(self):
        qty=1
        for d in self.dimensions:
            qty=qty*d.quantity
        if qty != self.product_visible_qty:
            self.product_visible_qty=qty
    
    @api.returns('self')
    @api.onchange('dimensions')
    def onchange_dimensions(self):
        qty=1
        for d in self.dimensions:
            qty=qty*d.quantity
        if qty != self.product_uom_qty:
            self.product_uom_qty=qty
    
    @api.returns('self')
    @api.multi
    @api.onchange('product_uom')
    def onchange_product_uom(self):
        self.dimensions=[]
        if self.product_uom.id:
            for d in self.product_uom.dimensions:
                new_dimension = self.dimensions.new({'dimension':d.id,'quantity':1,'sale_order_line': self.id})
                self.dimensions=self.dimensions | new_dimension
        return self.product_uom_change(pricelist=self.order_id.pricelist_id.id, product=self.product_id.id,
                                qty=self.product_uom_qty, uom=self.product_uom.id, qty_uos=self.product_uos_qty,
                                uos=self.product_uos.id, name=self.name, partner_id=self.order_id.partner_id.id,
                                lang=False, update_tax=True, date_order=self.order_id.date_order)
sale_order_line()

class sale_order_line_dimension(models.Model):
    _name = "sale.order.line.dimension"
    dimension = fields.Many2one('product.uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True, default=1)
    sale_order_line = fields.Many2one('sale.order.line','Order Line', required=True, ondelete='cascade')
        
sale_order_line_dimension()