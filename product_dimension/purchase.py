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

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    dimensions = fields.One2many('purchase.order.line.dimension','sale_order_line')
    product_visible_qty = fields.Float('Quantité', digits_compute= dp.get_precision('Product UoS'), compute='get_visible_qty')
    product_dimension_qty = fields.Integer('Quantité', required=True, default=0)
    
    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        res=super(SaleOrderLine,self)._prepare_order_line_procurement(group_id)
        res['product_dimension_qty'] = self.product_dimension_qty
        res['dimensions'] = [(0, 0, {'dimension': d.dimension.id, 'quantity': d.quantity, 'extrapolated_qty': d.extrapolated_qty, 'procurement_order': False})  for d in self.dimensions]
        return res
    

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        name = self.product_id.name
        if self.product_id.description_sale:
            name += '\n' + self.product_id.description_sale
        self.name = name
        return res

    @api.one
    @api.onchange('dimensions','product_dimension_qty')
    def onchange_set_name(self):
        if self.product_id:
            if self.dimensions:
                str_dim='('
                for d in self.dimensions:
                    str_dim += str(d.quantity) + d.dimension.name + '*'
                str_dim = str_dim[:-1] + ')'
                name = str(self.product_dimension_qty) + ' ' + self.product_id.name + '(s) ' + str_dim
                if self.product_id.description_sale:
                    name += '\n' + self.product_id.description_sale
                self.name = name

    @api.one
    def get_visible_qty(self):
        self.product_visible_qty = self.product_uom_qty
    
    @api.onchange('dimensions', 'product_dimension_qty')
    def onchange_dimensions(self):
        qty=self.product_dimension_qty
        for d in self.dimensions:
            qty *= d.quantity / d.dimension.multiplier
        if qty != self.product_uom_qty:
            self.product_uom_qty=qty
            self.product_visible_qty=qty
    
    @api.onchange('product_uom')
    @api.one
    def onchange_product_uom(self):
        self.dimensions=[]
        if self.product_uom.id:
            for d in self.product_uom.dimensions:
                new_dimension = self.dimensions.new({'dimension':d.id,'quantity':1,'sale_order_line': self.id})
                self.dimensions=self.dimensions | new_dimension
PurchaseOrderLine()

class PurchaseOrderLineDimension(models.Model):
    _name = "sale.order.line.dimension"
    dimension = fields.Many2one('product.uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', digits_compute= dp.get_precision('Product UoS'), required=True)
    sale_order_line = fields.Many2one('sale.order.line', required=True, ondelete='cascade')
    extrapolated_qty = fields.Integer(string='Quantité extrapolée', required=True)

    @api.one
    @api.onchange('extrapolated_qty')
    def onchange_extrapolated_qty(self):
        if self.dimension.rounding!=0:
            self.quantity = self.extrapolated_qty * self.dimension.rounding
        else:
            self.quantity = self.extrapolated_qty

    @api.one
    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.dimension.rounding !=0:
            self.extrapolated_qty = round(self.quantity / self.dimension.rounding)
            rounded_qty = self.extrapolated_qty * self.dimension.rounding
            if rounded_qty != self.quantity:
                self.quantity = rounded_qty
        else:
            self.extrapolated_qty = self.quantity
        
PurchaseOrderLineDimension()