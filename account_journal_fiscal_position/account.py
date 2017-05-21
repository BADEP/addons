# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from openerp.osv import osv
from openerp.addons.product import _common

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    fiscal_position = fields.Many2one('account.fiscal.position', related='journal_id.fiscal_position', readonly=True, store=False)

class AccountMoveLine(models.Model):
    _inherit = 'account.move'
    
    fiscal_position = fields.Many2one('account.fiscal.position', related='journal_id.fiscal_position', readonly=True, store=False)

class AccountInvoice(models.Model):
    _inherit ='account.invoice'
    
    fiscal_position = fields.Many2one('account.fiscal.position', related='journal_id.fiscal_position', readonly=True, store=True)
    
    @api.multi
    def invoice_pay_customer(self):
        res = super(AccountInvoice, self).invoice_pay_customer()
        res['context'].update({'fiscal_position': self.fiscal_position.id})
        return res

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    fiscal_position = fields.Many2one('account.fiscal.position')
    
class stock_invoice_onshipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'
    @api.model
    def _get_journal(self):
        active_ids = self.env.context.get('active_ids',[])
        journal_type = self._get_journal_type()
        pickings = self.env['stock.picking'].browse(active_ids)
        picking = pickings and pickings[0]
        if picking:
            if picking.sale_id:
                if picking.sale_id.fiscal_position:
                    journals = self.env['account.journal'].search(['&', ('type', '=', journal_type), ('fiscal_position', '=', picking.sale_id.fiscal_position.id)])
                    return journals and journals[0] or False
        journal_type = self._get_journal_type()
        journals = self.env['account.journal'].search([('type', '=', journal_type)])
        return journals and journals[0] or False
    
    journal_id = fields.Many2one('account.journal', 'Destination Journal', required=True, default=_get_journal)


class sale_order(models.Model):
    _inherit = 'sale.order'
    @api.model
    def _prepare_invoice(self, order, lines):
        res = super(sale_order, self)._prepare_invoice(order, lines)
        journals = self.env['account.journal'].search(['&', ('type', '=', 'sale'), ('fiscal_position', '=', order.fiscal_position.id)])
        if journals:
            res.update({'journal_id': journals[0].id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
