# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    amount_received = fields.Monetary(string=u'Total Delivered', store=True, readonly=True, compute='_amount_received_invoiced', track_visibility='always')
    amount_invoiced = fields.Monetary(string=u'Total Invoiced', store=True, readonly=True, compute='_amount_received_invoiced', track_visibility='always')
    
    @api.depends('order_line.price_received', 'order_line.price_invoiced')
    def _amount_received_invoiced(self):
        amount_received = amount_invoiced = 0
        for order in self:
            order.update({
                'amount_received': sum(order.order_line.mapped('price_received')),
                'amount_invoiced': sum(order.order_line.mapped('price_invoiced')),
            })

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_received = fields.Monetary(compute='_compute_amount_received_invoiced', string='Amount Delivered', readonly=True, store=True)
    price_invoiced = fields.Monetary(compute='_compute_amount_received_invoiced', string='Amount Invoiced', readonly=True, store=True)

    @api.depends('price_total', 'qty_received', 'qty_invoiced')
    def _compute_amount_received_invoiced(self):
        for line in self:
            line.update({
                'price_received': line.price_total * (line.qty_received / line.product_uom_qty) if line.product_uom_qty else 0,
                'price_invoiced': line.price_total * (line.qty_invoiced / line.product_uom_qty) if line.product_uom_qty else 0,
            })