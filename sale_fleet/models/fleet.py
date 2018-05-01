# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    def _get_current_company(self):
        return self.env.user.company_id.id
    
    sale_orders = fields.One2many('sale.order', 'vehicle', string='Sales')
    sales_amount = fields.Monetary(currency_field='currency_id', compute='get_sales', store=False)
    sales_count = fields.Integer(compute='get_sales', store=False)
    sale_ok = fields.Boolean(string='Available in Sales',default=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    company_id = fields.Many2one('res.company', default=_get_current_company)

    @api.one
    @api.depends('sale_orders')
    def get_sales(self):
        self.sales_amount = sum(order.amount_total for order in self.sale_orders.filtered(lambda s: s.state in ('sale', 'done')))
        self.sales_count = len(self.sale_orders.filtered(lambda s: s.state in ('sale', 'done')))

    @api.multi
    def act_show_sales(self):
        action = self.env.ref('sale.action_orders')

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
        result['domain'] = "[('id','in',["+','.join(map(str, self.sale_orders.ids))+"])]"
        return result