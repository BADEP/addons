# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    vehicle = fields.Many2one('fleet.vehicle', domain=[('invoice_ok','=',True)], readonly=True, states={'draft': [('readonly', False)]})
    driver = fields.Many2one('res.partner', readonly=True, states={'draft': [('readonly', False)]})
    
    @api.onchange('vehicle')
    def set_driver(self):
        if self.vehicle and self.vehicle.driver_id:
            self.driver = self.vehicle.driver_id
        else:
            self.driver = False

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"
    vehicle = fields.Many2one('fleet.vehicle', readonly=True)
    driver = fields.Many2one('res.partner', readonly=True)
    
    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ai.vehicle, ai.driver"
    
    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.vehicle as vehicle, sub.driver as driver"
    
    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", ai.vehicle as vehicle, ai.driver as driver"


    
    