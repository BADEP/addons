# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2016-2016 BADEP. All Rights Reserved.
#    Author: Khalid HAZAM <k.hazam@badep.ma>
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

import logging
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from itertools import groupby
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class SaleWorkflowProcess(models.Model):
    _inherit = 'sale.workflow.process'

    create_invoice = fields.Boolean(default=False, string='Facturation automatique')
    create_invoice_grouped = fields.Boolean(default=False, string='Facturation groupée')
    create_invoice_day = fields.Integer(default=1, string='Jour de facturation')

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    display_ref = fields.Boolean(default=True, string='Référence produit')
    display_photo = fields.Boolean(default=False, string='Photo produit')
    display_discount = fields.Boolean(default=False, string='Remise')
    margin_percentage = fields.Char(string="Marge (%)", compute='get_margin_percentage', digits_compute=dp.get_precision('Account'))

    @api.one
    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id and self.project_id.workflow_process:
            self.workflow_process_id = self.project_id.workflow_process
        else:
            self.workflow_process_id = self.partner_id.workflow_process
    
    @api.one
    @api.depends('margin', 'amount_untaxed')
    def get_margin_percentage(self):
        if self.amount_untaxed != 0:
            self.margin_percentage = round((self.margin / self.amount_untaxed) * 100, 2)


    """Get partner configuration: Note, workflow"""
    @api.multi
    def onchange_partner_id(self, part):
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False, 'payment_term': False, 'fiscal_position': False}}
        
        val = super(SaleOrder, self).onchange_partner_id(part)
        part = self.env['res.partner'].browse(part)
        
        val.get('value', {}).update({'note': part.comment})
        
        if self.project_id and self.project_id.workflow_process:
            workflow_process_id = self.project_id.workflow_process
        else:
            workflow_process_id = part.workflow_process
        val.get('value', {}).update({'workflow_process_id': workflow_process_id})
        return val
    
    
    """Propagate layout to procurement (and therefore to pickings)"""
    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res = super(SaleOrder, self)._prepare_order_line_procurement(order, line, group_id)
        res['sale_layout_cat_id'] = line.sale_layout_cat_id.id
        res['categ_sequence'] = line.categ_sequence
        return res

    @api.multi
    def action_ship_create(self):
        """Propagate note to shipping and assign available stock"""
        res = super(SaleOrder, self).action_ship_create()
        for order in self:
            order.picking_ids.write({'note': order.note})
            order.picking_ids.action_assign()
        return res

    @api.multi
    def _detect_exceptions(self, order_exceptions,
                           line_exceptions):
        self.ensure_one()
        res = super(SaleOrder, self)._detect_exceptions(order_exceptions, line_exceptions)
        for order_line in self.order_line:
            exception_ids = []
            for rule in line_exceptions:
                if self._rule_eval(rule, 'line', order_line):
                    exception_ids.append(rule.id)
            order_line.exception_ids = [(6, 0, exception_ids)]
        return res
    
   
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    exception_ids = fields.Many2many(
        'sale.exception',
        'sale_order_line_exception_rel', 'sale_order_line_id', 'exception_id',
        string='Exceptions')
    
    has_exception = fields.Boolean(compute='get_has_exception', default=True)
    quantity_in_stock = fields.Float(string='Quantité en Stock', digits_compute=dp.get_precision('Product UoS'), related='product_id.qty_available', store=True)
    quantity_forecast = fields.Float(string='Quantité prévue', digits_compute=dp.get_precision('Product UoS'), compute='get_forecast_data',store=True)
    quantity_unreserved = fields.Float(string='Quantité non réservée', digits_compute=dp.get_precision('Product UoS'), related='product_id.qty_available_not_res',store=True)
    date_expected = fields.Date(string="Date prévue", compute='get_forecast_data')
    margin_percentage = fields.Char(string="Marge (%)", compute='get_margin_percentage', digits_compute=dp.get_precision('Account')) 
    
    @api.one
    @api.depends('exception_ids')
    def get_has_exception(self):
        if self.exception_ids:
            self.has_exception = True
        else:
            self.has_exception = False

    @api.one
    @api.depends('margin', 'price_subtotal')
    def get_margin_percentage(self):
        if self.price_subtotal != 0:
            self.margin_percentage = round((self.margin / self.price_subtotal) * 100, 2)
    
    """Get forecast qty"""
    @api.one
    @api.depends('delay','product_id','order_id.date_order')
    def get_forecast_data(self):
        self.date_expected = fields.Datetime.to_string(fields.Datetime.from_string(self.order_id.date_order) + relativedelta(days=self.delay))
        self.quantity_forecast = self.product_id and self.product_id.with_context({'date_expected': self.date_expected}).virtual_available or 0

    """1)Display only product name without ref
    2)Calculate available qty and forecast qty for the prodct"""    
    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):
        ctx = self.env.context.copy()
        ctx.update({'display_default_code': False})
        product_obj = self.env['product.product'].browse(product)
        result = super(SaleOrderLine, self.with_context(ctx)).product_id_change(pricelist, product, qty, uom, qty_uos, uos, name,
                                        partner_id, lang, update_tax, date_order, packaging,
                                        fiscal_position, flag)
        result['value'].update({'quantity_in_stock': product_obj.qty_available, 'quantity_forecast': self.quantity_forecast})
        return result
    
    
    """"Disable out of stock warning
    TODO: Only disable if the product is mto or mts+mto"""
    @api.multi
    def _check_routing(self, product, warehouse_id):
        return True

class SaleException(models.Model):
    _inherit = 'sale.exception'

    """Link Exceptions to order lines"""
    sale_order_line_ids = fields.Many2many(
        'sale.order.line',
        'sale_order_line_exception_rel', 'exception_id', 'sale_order_line_id',
        string='Lignes de commande',
        readonly=True)