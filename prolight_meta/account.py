# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2016-2016 BADEP. All Rights Reserved.
#    Author: Khalid HAZAM <k.hazam@badep.ma>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    workflow_process = fields.Many2one('sale.workflow.process', string="Flux automatique")
    
    @api.multi
    def on_change_partner_id(self, partner_id, name):
        res=super(AccountAnalyticAccount, self).on_change_partner_id(partner_id, name)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
        res.get('value', {}).update({'workflow_process': partner.workflow_process})
        return res
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    display_ref = fields.Boolean(default=True, string='Référence produit')
    display_photo = fields.Boolean(default=True, string='Photo produit')
    display_discount = fields.Boolean(default=True, string='Remise')

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    amount_taxes = fields.Float(string='Taxes', digits_compute=dp.get_precision('Product UoS'), compute='get_amount_taxes')
    
    @api.one
    @api.depends('discount', 'price_unit', 'invoice_line_tax_id', 'product_id', 'quantity')
    def get_amount_taxes(self):
        self.amount_taxes = self.invoice_line_tax_id.compute_all(self.price_unit * (1 - (self.discount or 0.0) / 100.0),
                                                                 self.quantity,
                                                                 product=self.product_id,
                                                                 partner=self.invoice_id.partner_id)['total_included'] - \
                            self.invoice_line_tax_id.compute_all(self.price_unit * (1 - (self.discount or 0.0) / 100.0),
                                                                 self.quantity,
                                                                 product=self.product_id,
                                                                 partner=self.invoice_id.partner_id)['total']