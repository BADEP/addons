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

class ProcurementOrderAttribute(models.Model):
    _inherit = 'procurement.order.attribute'

    custom_value = fields.Float(string='Custom value')
    attr_type = fields.Selection(string='Type', store=False,
                                 related='attribute.attr_type')

    def _is_custom_value_in_range(self):
        if self.attr_type == 'range':
            return (self.value.min_range <= self.custom_value <=
                    self.value.max_range)
        return True

    @api.one
    @api.constrains('custom_value', 'attr_type', 'value')
    def _custom_value_in_range(self):
        if not self._is_custom_value_in_range():
            raise exceptions.Warning(
                _("Custom value for attribute '%s' must be between %s and"
                  " %s.")
                % (self.attribute.name, self.value.min_range,
                   self.value.max_range))

    @api.one
    @api.onchange('custom_value', 'value')
    def _onchange_custom_value(self):
        self._custom_value_in_range()

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)
        res['product_template'] = procurement.product_template.id
        res['product_attributes'] = [(0, 0, {'attribute': x.attribute.id, 'value': x.value.id, 'custom_value': x.custom_value}) for x in procurement.product_attributes]
        return res