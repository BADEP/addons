# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, exceptions, _
from openerp.addons import decimal_precision as dp


class ProductAttributeValueProcurementOrder(models.Model):
    _name = 'procurement.order.attribute'

    @api.one
    @api.depends('attribute', 'procurement_order.product_template',
                 'procurement_order.product_template.attribute_line_ids')
    def _get_possible_attribute_values(self):
        attr_values = self.env['product.attribute.value']
        for attr_line in self.procurement_order.product_id.product_tmpl_id.attribute_line_ids:
            if attr_line.attribute_id.id == self.attribute.id:
                attr_values |= attr_line.value_ids
        self.possible_values = attr_values.sorted()

    procurement_order = fields.Many2one(
        comodel_name='procurement.order', string='Order line')
    attribute = fields.Many2one(
        comodel_name='product.attribute', string='Attribute')
    value = fields.Many2one(
        comodel_name='product.attribute.value', string='Value',
        domain="[('id', 'in', possible_values[0][2])]")
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values', readonly=True)

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    product_template = fields.Many2one(
        comodel_name='product.template', string='Product Template',
        readonly=False, states={'done': [('readonly', True)]})
    product_attributes = fields.One2many(
        comodel_name='procurement.order.attribute', inverse_name='procurement_order',
        string='Product attributes', copy=True,
        readonly=False, states={'done': [('readonly', True)]})
    # Neeeded because one2many result type is not constant when evaluating
    # visibility in XML
    product_attributes_count = fields.Integer(
        compute="_get_product_attributes_count")
    product_id = fields.Many2one(
        domain="[('product_tmpl_id', '=', product_template)]")

    @api.one
    @api.depends('product_attributes')
    def _get_product_attributes_count(self):
        self.product_attributes_count = len(self.product_attributes)

    @api.model
    def _order_attributes(self, template, product_attribute_values):
        res = template._get_product_attributes_dict()
        res2 = []
        for val in res:
            value = product_attribute_values.filtered(
                lambda x: x.attribute_id.id == val['attribute'])
            if value:
                val['value'] = value
                res2.append(val)
        return res2

    @api.multi
    def onchange_product_id(
            self, product):
        product_obj = self.env['product.product']
        res = super(ProcurementOrder, self).onchange_product_id(product)
        if product:
            product = product_obj.browse(product)
            res['value']['product_attributes'] = (
                product._get_product_attributes_values_dict())
        return res

    @api.multi
    @api.onchange('product_template')
    def onchange_product_template(self):
        self.ensure_one()
        self.name = self.product_template.name
        if not self.product_template.attribute_line_ids:
            self.product_id = (
                self.product_template.product_variant_ids and
                self.product_template.product_variant_ids[0])
        else:
            self.product_id = False
        self.product_attributes = (
            [(2, x.id) for x in self.product_attributes] +
            [(0, 0, x) for x in
             self.product_template._get_product_attributes_dict()])

    @api.one
    @api.onchange('product_attributes')
    def onchange_product_attributes(self):
        product_obj = self.env['product.product']
        self.product_id = product_obj._product_find(
            self.product_template, self.product_attributes)
    
    @api.one
    def _check_line_confirmability(self):
        if any(not bool(line.value) for line in self.product_attributes):
            raise exceptions.Warning(
                _("You can not confirm before configuring all attribute "
                  "values."))
            
    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)
        res['product_template'] = procurement.product_template.id
        res['product_attributes'] = [(0, 0, {'attribute': x.attribute.id, 'value': x.value.id}) for x in procurement.product_attributes]
        return res