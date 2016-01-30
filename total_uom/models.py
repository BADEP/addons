# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    total_uoms = fields.One2many('product.uom.total', 'sale_order', compute='get_total_uoms', string='Total par unité')
    
    @api.one
    @api.depends('order_line')
    def get_total_uoms(self):
        uoms = self.order_line.mapped('product_uom.id')
        for uom in uoms:
            self.total_uoms |= self.env['product.uom.total'].new({'uom': uom,
                                                                     'quantity': sum(x.product_uom_qty for x in self.order_line.filtered(lambda r: r.product_uom.id==uom)),
                                                                     'sale_order': self.id
                                                                     })

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    total_uoms = fields.One2many('product.uom.total', 'stock_picking', compute='get_total_uoms', string='Total par unité')
    
    @api.one
    @api.depends('move_lines')
    def get_total_uoms(self):
        uoms = self.move_lines.mapped('product_uom.id')
        for uom in uoms:
            self.total_uoms |= self.env['product.uom.total'].create({'uom': uom,
                                                                     'quantity': sum(x.product_uom_qty for x in self.move_lines.filtered(lambda r: r.product_uom.id==uom)),
                                                                     'stock_picking': self.id
                                                                     })

class ProductUomTotal(models.Model):
    _name = 'product.uom.total'
    
    sale_order = fields.Many2one('sale.order', string='Bon de commande')
    stock_picking = fields.Many2one('stock.picking')
    uom = fields.Many2one('product.uom', string='Unité')
    quantity = fields.Float(string='Quantité', digits_compute=dp.get_precision('Product UoS'))