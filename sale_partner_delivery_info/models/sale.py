# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        values = {
            'warehouse_id': self.partner_id and self.partner_id.warehouse_id and self.partner_id.warehouse_id.id or self.env['stock.warehouse'].search()[0],
        }
        self.update(values)