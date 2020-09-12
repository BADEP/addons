# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

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


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    price_received = fields.Float('Total livré', readonly=True)
    price_invoiced = fields.Float('Total facturé', readonly=True)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
                SELECT
                    po.id as order_id,
                    min(l.id) as id,
                    po.date_order as date_order,
                    po.state,
                    po.date_approve,
                    po.dest_address_id,
                    po.partner_id as partner_id,
                    po.user_id as user_id,
                    po.company_id as company_id,
                    po.fiscal_position_id as fiscal_position_id,
                    l.product_id,
                    p.product_tmpl_id,
                    t.categ_id as category_id,
                    po.currency_id,
                    t.uom_id as product_uom,
                    extract(epoch from age(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2) as delay,
                    extract(epoch from age(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
                    count(*) as nbr_lines,
                    sum(l.price_total / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as price_total,
                    sum(l.price_received / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as price_received,
                    sum(l.price_invoiced / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as price_invoiced,
                    (sum(l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2) as price_average,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    analytic_account.id as account_analytic_id,
                    sum(p.weight * l.product_qty/line_uom.factor*product_uom.factor) as weight,
                    sum(p.volume * l.product_qty/line_uom.factor*product_uom.factor) as volume,
                    sum(l.price_subtotal / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as untaxed_total,
                    sum(l.product_qty / line_uom.factor * product_uom.factor) as qty_ordered,
                    sum(l.qty_received / line_uom.factor * product_uom.factor) as qty_received,
                    sum(l.qty_invoiced / line_uom.factor * product_uom.factor) as qty_billed,
                    case when t.purchase_method = 'purchase' 
                         then sum(l.product_qty / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                         else sum(l.qty_received / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                    end as qty_to_be_billed
        """ % self.env['res.currency']._select_companies_rates()
        return select_str