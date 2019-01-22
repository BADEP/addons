# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_delivered = fields.Monetary(string=u'Total livré', store=True, readonly=True, compute='_amount_delivered_invoiced', track_visibility='always')
    amount_invoiced = fields.Monetary(string=u'Total facturé', store=True, readonly=True, compute='_amount_delivered_invoiced', track_visibility='always')
    
    @api.depends('order_line.price_delivered', 'order_line.price_invoiced')
    def _amount_delivered_invoiced(self):
        amount_delivered = amount_invoiced = 0
        for order in self:
            for line in order.order_line:
                amount_delivered += line.price_delivered
                amount_invoiced += line.price_invoiced
            order.update({
                'amount_delivered': amount_delivered,
                'amount_invoiced': amount_invoiced,
            })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_delivered = fields.Monetary(compute='_compute_amount_delivered_invoiced', string='Total delivered', readonly=True, store=True)
    price_invoiced = fields.Monetary(compute='_compute_amount_delivered_invoiced', string='Total invoiced', readonly=True, store=True)

    @api.depends('price_total', 'qty_delivered', 'qty_invoiced')
    def _compute_amount_delivered_invoiced(self):
        for line in self:
            line.update({
                'price_delivered': line.price_total * (line.qty_delivered / line.product_uom_qty),
                'price_invoiced': line.price_total * (line.qty_invoiced / line.product_uom_qty),
            })