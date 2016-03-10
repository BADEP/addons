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


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res = super(SaleOrder, self)._prepare_order_line_procurement(order, line, group_id)
        res['product_dimension_qty'] = line.product_dimension_qty
        res['dimensions'] = [(0, 0, {'dimension': d.dimension.id, 'quantity': d.quantity})  for d in line.dimensions]
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    dimensions = fields.One2many('sale.order.line.dimension', 'sale_order_line', readonly=True, states={'draft': [('readonly', False)]})
    product_visible_qty = fields.Float('Quantité', compute='get_visible_qty')
    product_dimension_qty = fields.Integer('Quantité', required=True, default=1)

    
    @api.one
    @api.depends('product_uom_qty')
    def get_visible_qty(self):
        self.product_visible_qty = self.product_uom_qty
    
    @api.one
    @api.onchange('dimensions', 'product_dimension_qty')
    def onchange_dimensions(self):
        qty = self.product_dimension_qty
        for d in self.dimensions:
            qty *= d.quantity / d.dimension.multiplier
        if qty != self.product_uom_qty:
            self.product_uom_qty = qty

    @api.one
    @api.onchange('dimensions', 'product_dimension_qty')
    def onchange_set_name(self):
        if self.product_id:
            if self.dimensions:
                str_dim=' | '
                for d in self.dimensions:
                    str_dim += str(d.quantity) + '*'
                str_dim = str_dim[:-1]
                self.name = str(self.product_dimension_qty) + ' ' + self.product_id.with_context({'display_default_code': False}).name_get()[0][1] + str_dim

    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):
        return super(SaleOrderLine, self.with_context({'display_default_code': False})).product_id_change(pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag)
        
    @api.multi
    def onchange_product_uom(self, pricelist, product, qty=0,
                             uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                             lang=False, update_tax=True, date_order=False, fiscal_position=False, context=None):
        res = super(SaleOrderLine, self).onchange_product_uom(pricelist=pricelist, product=product, qty=qty,
                                                              uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                                                              lang=lang, update_tax=update_tax, date_order=date_order, fiscal_position=fiscal_position)
        if uom:
            res['value'].update(dimensions = [(0, 0, {'dimension':d.id, 'quantity':d.multiplier, 'sale_order_line': self.id}) for d in self.env['product.uom'].browse(uom).dimensions])
        res['value'].update(product_dimension_qty = qty)
        return res

class SaleOrderLineDimension(models.Model):
    _name = "sale.order.line.dimension"
    dimension = fields.Many2one('product.uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', digits_compute=dp.get_precision('Product UoS'), required=True)
    sale_order_line = fields.Many2one('sale.order.line', required=True, ondelete='cascade')
    extrapolated_qty = fields.Integer(string='Quantité extrapolée', compute='get_extrapolated_qty')

    @api.one
    @api.depends('quantity')
    def get_extrapolated_qty(self):
        if self.dimension.rounding != 0:
            self.extrapolated_qty = round(self.quantity / self.dimension.rounding)
        else:
            self.extrapolated_qty = self.quantity + self.dimension.offset
