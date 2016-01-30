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


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'
    
    discount_lines = fields.One2many('account.payment.term.discount', 'payment_term')
    
    def get_appropriate_discount(self, amount):
        discount = 0
        ceil = 0
        for line in self.discount_lines:
            if line.ceil < amount and line.ceil > ceil:
                ceil = line.ceil
                discount = line.discount
        return discount
AccountPaymentTerm()

class AccountPaymentTermDiscount(models.Model):
    _name = 'account.payment.term.discount'
    
    payment_term = fields.Many2one('account.payment.term', required=True)
    ceil = fields.Float(digits_compute=dp.get_precision('Account'), required=True)
    discount = fields.Float(required=True)
AccountPaymentTermDiscount()

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.onchange('payment_term')
    def onchange_set_discount(self):
        if self.payment_term:
            self.global_discount = self.payment_term.get_appropriate_discount(self.amount_total)
        else:
            self.global_discount = 0
SaleOrder()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
