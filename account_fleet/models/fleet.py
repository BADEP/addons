# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    def _get_current_company(self):
        return self.env.user.company_id.id
    
    invoices = fields.One2many('account.invoice', 'vehicle', string='Invoices')
    invoices_sale_amount = fields.Monetary(currency_field='currency_id', compute='get_invoicing', store=False)
    invoices_purchase_amount = fields.Monetary(currency_field='currency_id', compute='get_invoicing', store=False)
    invoices_sale_count = fields.Integer(compute='get_invoicing', store=False)
    invoices_purchase_count = fields.Integer(compute='get_invoicing', store=False)
    invoice_ok = fields.Boolean(string='Available in Invoicing',default=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    company_id = fields.Many2one('res.company', default=_get_current_company)

    @api.one
    @api.depends('invoices')
    def get_invoicing(self):
        self.invoices_sale_amount = sum(invoice.amount_total for invoice in self.invoices.filtered(lambda s: s.state in ('open', 'paid') and s.type in ('out_invoice', 'out_refund')))
        self.invoices_sale_count = len(self.invoices.filtered(lambda s: s.state in ('open', 'paid') and s.type in ('out_invoice', 'out_refund')))
        self.invoices_purchase_amount = sum(invoice.amount_total for invoice in self.invoices.filtered(lambda s: s.state in ('open', 'paid') and s.type in ('in_invoice', 'in_refund')))
        self.invoices_purchase_count = len(self.invoices.filtered(lambda s: s.state in ('open', 'paid') and s.type in ('in_invoice', 'in_refund')))

    @api.multi
    def act_show_sale_invoices(self):
        action = self.env.ref('account.action_invoice_tree1')

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
        result['domain'] = "[('id','in',["+','.join(map(str, self.invoices.ids))+"]),('type', 'in', ('out_invoice', 'out_refund'))]"
        return result
    @api.multi
    def act_show_purchase_invoices(self):
        action = self.env.ref('account.action_invoice_tree2')

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
        result['domain'] = "[('id','in',["+','.join(map(str, self.invoices.ids))+"]),('type', 'in', ('in_invoice', 'in_refund'))]"
        return result