# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    amount_received = fields.Monetary(string=u'Total Delivered', store=True, readonly=True, compute='_amount_received_invoiced')
    amount_to_receive = fields.Monetary(string=u'Total To Receive', store=True, readonly=True, compute='_amount_received_invoiced')
    amount_invoiced = fields.Monetary(string=u'Total Invoiced', store=True, readonly=True, compute='_amount_received_invoiced')
    amount_uninvoiced = fields.Monetary(string=u'Total Uninvoiced', store=True, readonly=True, compute='_amount_received_invoiced')

    @api.depends('order_line.price_received', 'order_line.price_invoiced')
    def _amount_received_invoiced(self):
        for order in self:
            order.update({
                'amount_received': sum(order.order_line.mapped('price_received')),
                'amount_to_receive': sum(order.order_line.mapped('price_to_receive')),
                'amount_invoiced': sum(order.order_line.mapped('price_invoiced')),
                'amount_uninvoiced': sum(order.order_line.mapped('price_uninvoiced')),
            })

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_received = fields.Monetary(compute='_compute_amount_received_invoiced', string='Amount Delivered', readonly=True, store=True)
    price_to_receive = fields.Monetary(compute='_compute_amount_received_invoiced', string='Amount To Receive', readonly=True, store=True)
    price_invoiced = fields.Monetary(compute='_compute_amount_received_invoiced', string='Amount Invoiced', readonly=True, store=True)
    price_uninvoiced = fields.Monetary(compute='_compute_amount_received_invoiced', string='Amount Uninvoiced', readonly=True, store=True)

    @api.depends('price_total', 'qty_received', 'qty_invoiced')
    def _compute_amount_received_invoiced(self):
        for line in self:
            line.update({
                'price_received': line.price_total * (line.qty_received / line.product_qty) if line.product_qty else 0,
                'price_to_receive': line.price_total * ((line.product_qty - line.qty_received) / line.product_qty) if line.product_qty else 0,
                'price_invoiced': line.price_total * (line.qty_invoiced / line.product_qty) if line.product_qty else 0,
                'price_uninvoiced': (line.price_total * (line.qty_received / line.product_qty) - line.price_total * (line.qty_invoiced / line.product_qty)) if line.product_qty else 0,
            })


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    price_received = fields.Float('Total livré', readonly=True)
    price_to_receive = fields.Float('Total à réceptionner', readonly=True)
    price_invoiced = fields.Float('Total facturé', readonly=True)
    price_uninvoiced = fields.Float('Total non facturé', readonly=True)

    def _select(self):
        return super()._select() + """, sum(l.price_received / COALESCE(po.currency_rate, 1.0))::decimal(16,2) * currency_table.rate as price_received,
                                        sum(l.price_to_receive / COALESCE(po.currency_rate, 1.0))::decimal(16,2) * currency_table.rate as price_to_receive,
                                        sum(l.price_invoiced / COALESCE(po.currency_rate, 1.0))::decimal(16,2) * currency_table.rate as price_invoiced,
                                        sum(l.price_uninvoiced / COALESCE(po.currency_rate, 1.0))::decimal(16,2) * currency_table.rate as price_uninvoiced"""
