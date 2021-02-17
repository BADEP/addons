# -*- coding: utf-8 -*-

import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo import models, fields


# TODO add a field price_unit_uos
# - update it on change product and unit price
# - use it in report if there is a uos
class sale_order_line(models.Model):
    
    def _amount_total(self):
        tax_obj = self.env['account.tax']
        cur_obj = self.env['res.currency']
        res = {}
        for line in self.browse():
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cur, taxes['total_included'])
        return res

    _inherit = 'sale.order.line'

    price_total = fields.Float(string='Total', compute='_amount_total')

class account_invoice_line(models.Model):
    _inherit = 'account.move.line'
    
    def _amount_total(self):
        tax_obj = self.env['account.tax']
        cur_obj = self.env['res.currency']
        res = {}
        for line in self.browse():
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(line.invoice_line_tax_id, price, line.quantity, line.product_id, line.invoice_id.partner_id)
            cur = line.invoice_id.currency_id
            res[line.id] = cur_obj.round(cur, taxes['total_included'])
        return res

    price_total = fields.Float(string='Total', compute='_amount_total')
