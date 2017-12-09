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
from openerp import tools
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    partner_sage = fields.Char(compute='get_partner_sage', string='Tier Sage')
    date_sage = fields.Date(compute='get_date_sage')

    @api.one
    @api.depends('date', 'period_id')
    def get_date_sage(self):
        self.date_sage = self.date if self.date < self.period_id.date_stop else self.period_id.date_stop

    @api.one
    @api.depends('partner_id')
    def get_partner_sage(self):
        if self.partner_id and self.account_id.type == 'receivable':
            self.partner_sage = self.partner_id.code_c_sage
        if self.partner_id and self.account_id.type == 'payable':
            self.partner_sage = self.partner_id.code_f_sage

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    delivery_address_id = fields.Many2one('res.partner', string='Adresse de livraison')
    consignee_id = fields.Many2one('res.partner', string='Bateau', domain=[('is_consignee', '=', True)])
    exchange_rate = fields.Float(string='Taux de change', readonly=True, digits=(12,6))
    amount_local = fields.Float(string='Montant en DH', digits=dp.get_precision('Account'), compute='compute_amount_local', store=True)
    with_rate = fields.Boolean(string='Imprimer le taux', default=False)

    @api.one
    @api.depends('exchange_rate', 'amount_total')
    def compute_amount_local(self):
        self.amount_local = self.exchange_rate * self.amount_total
    
    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for inv in self:
            inv.exchange_rate = self.currency_id and self.currency_id.with_context(date=self.date_invoice).rate_silent
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        res = super(StockPicking, self)._get_invoice_vals(key, inv_type, journal_id, move)
        res.update({'consignee_id': move.picking_id.consignee_id and move.picking_id.consignee_id.id,
                    'delivery_address_id': move.picking_id.delivery_address_id and move.picking_id.delivery_address_id.id,
                    })
        return res

class ResPartner(models.Model):
    _inherit = 'res.partner'
    code_c_sage = fields.Char(string='Code Client Sage', compute='get_codes_sage')
    code_f_sage = fields.Char(string='Code Fournisseur Sage', compute='get_codes_sage')

    @api.depends('ref', 'name')
    @api.one
    def get_codes_sage(self):
        self.code_c_sage = (self.ref if self.ref else self.name) + " - Client"
        self.code_f_sage = (self.ref if self.ref else self.name) + " - Fournisseur"

    @api.onchange('is_consignee')
    def onchange_is_consignee(self):
        if self.is_consignee:
            self.is_company = True if self.is_consignee else False
            
class account_invoice_report(models.Model):
    _inherit = "account.invoice.report"

    @api.cr
    def init(self, cr):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            WITH currency_rate (currency_id, rate, date_start, date_end) AS (
                SELECT r.currency_id, 1/r.rate, r.name AS date_start,
                    (SELECT name FROM res_currency_rate r2
                     WHERE r2.name > r.name AND
                           r2.currency_id = r.currency_id
                     ORDER BY r2.name ASC
                     LIMIT 1) AS date_end
                FROM res_currency_rate r
            )
            %s
            FROM (
                %s %s %s
            ) AS sub
            JOIN currency_rate cr ON
                (cr.currency_id = sub.currency_id AND
                 cr.date_start <= COALESCE(sub.date, NOW()) AND
                 (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
        )""" % (
                    self._table,
                    self._select(), self._sub_select(), self._from(), self._group_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
