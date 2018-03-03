# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    def _get_current_company(self):
        return self.env.user.company_id.id
    
    purchase_orders = fields.One2many('purchase.order', 'vehicle', string='Purchases')
    purchases_amount = fields.Monetary(currency_field='currency_id', compute='get_purchases', store=False)
    purchases_count = fields.Integer(compute='get_purchases', store=False)
    purchase_ok = fields.Boolean(string='Available in Purchases',default=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    company_id = fields.Many2one('res.company', default=_get_current_company)

    @api.one
    @api.depends('purchase_orders')
    def get_purchases(self):
        self.purchases_amount = sum(order.amount_total for order in self.purchase_orders.filtered(lambda s: s.state in ('purchase', 'done')))
        self.purchases_count = len(self.purchase_orders.filtered(lambda s: s.state in ('purchase', 'done')))

    @api.multi
    def act_show_purchases(self):
        action = self.env.ref('purchase.purchase_form_action')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        result['domain'] = "[('id','in',["+','.join(map(str, self.purchase_orders.ids))+"])]"
        return result