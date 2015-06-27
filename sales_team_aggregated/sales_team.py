# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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
import calendar
from datetime import date
from dateutil import relativedelta
import json

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_repr


class crm_case_section(osv.osv):
    _inherit = "crm.case.section"

    def _get_sale_orders_data(self, cr, uid, ids, field_name, arg, context=None):
        obj = self.pool['sale.order']
        month_begin = date.today().replace(day=1)
        date_begin = (month_begin - relativedelta.relativedelta(months=self._period_number - 1)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        date_end = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

        res = {}
        for id in ids:
            res[id] = {}
            created_domain = [('section_id', 'child_of', id), ('state', 'in', ['draft','sent']), ('date_order', '>=', date_begin), ('date_order', '<=', date_end)]
            validated_domain = [('section_id', 'child_of', id), ('state', 'not in', ['draft', 'sent', 'cancel']), ('date_order', '>=', date_begin), ('date_order', '<=', date_end)]
            res[id]['monthly_quoted'] = json.dumps(self.__get_bar_values(cr, uid, obj, created_domain, ['amount_total', 'date_order'], 'amount_total', 'date_order', context=context))
            res[id]['monthly_confirmed'] = json.dumps(self.__get_bar_values(cr, uid, obj, validated_domain, ['amount_total', 'date_order'], 'amount_total', 'date_order', context=context))

        return res

    def _get_invoices_data(self, cr, uid, ids, field_name, arg, context=None):
        obj = self.pool['account.invoice.report']
        month_begin = date.today().replace(day=1)
        date_begin = (month_begin - relativedelta.relativedelta(months=self._period_number - 1)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        date_end = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

        res = {}
        for id in ids:
            created_domain = [('section_id', 'child_of', id), ('state', 'not in', ['draft', 'cancel']), ('date', '>=', date_begin), ('date', '<=', date_end)]
            values = self.__get_bar_values(cr, uid, obj, created_domain, ['price_total', 'date'], 'price_total', 'date', context=context)
            for value in values:
                value['value'] = float_repr(value.get('value', 0), precision_digits=self.pool['decimal.precision'].precision_get(cr, uid, 'Account'))
            res[id] = json.dumps(values)
        return res
    
    _columns = {
        'monthly_quoted': fields.function(_get_sale_orders_data,
            type='char', readonly=True, multi='_get_sale_orders_data',
            string='Rate of created quotation per duration'),
        'monthly_confirmed': fields.function(_get_sale_orders_data,
            type='char', readonly=True, multi='_get_sale_orders_data',
            string='Rate of validate sales orders per duration'),
        'monthly_invoiced': fields.function(_get_invoices_data,
            type='char', readonly=True,
            string='Rate of sent invoices per duration'),
    }
