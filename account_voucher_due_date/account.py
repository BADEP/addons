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

class account_voucher(models.Model):
    _inherit = 'account.voucher'
    
    @api.model
    def voucher_move_line_create(self, id, line_total, move_id, company_currency, current_currency):
        res = super(account_voucher, self).voucher_move_line_create(id, line_total, move_id, company_currency, current_currency)
        voucher = self.env['account.voucher'].browse(id)
        for line in self.env['account.move.line'].browse(res[1][0]):
            if line.journal_id.type == 'bank':
                line.date = voucher.date_due
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
