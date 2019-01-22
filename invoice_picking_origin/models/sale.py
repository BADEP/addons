# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'name': self.client_order_ref or ', '.join(self.picking_ids.mapped('name')) if self.picking_ids else ''})
        return res