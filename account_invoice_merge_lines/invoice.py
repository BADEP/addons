# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 BADEP. All Rights Reserved.
#    Author: Khalid Hazam<k.hazam@badep.ma>
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

from openerp import models, api
from openerp.osv.orm import browse_record, browse_null

INVOICE_LINE_KEY_COLS = ['discount', 'invoice_line_tax_id',
                        'price_unit', 'product_id',
                        'account_id', 'account_analytic_id']

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    
    @api.one
    def merge_lines(self):
        to_delete = []
        itered = []
        for line in self.invoice_line:
            itered.append(line.id)
            line_to_merge = self.invoice_line.search([('invoice_id', '=', self.id),
                                                      ('discount', '=', line.discount),
                                                      ('invoice_line_tax_id', '=', line.invoice_line_tax_id.id),
                                                      ('price_unit', '=', line.price_unit),
                                                      ('product_id', '=', line.product_id.id), 
                                                      ('account_id', '=', line.account_id.id),
                                                      ('account_analytic_id','=', line.account_analytic_id.id),
                                                      ('id','not in', itered)], limit=1)
            if line_to_merge:
                to_delete.append(line.id)
                line_to_merge.write({'quantity': line_to_merge.quantity + line.quantity,
                                     'origin': line_to_merge.origin + line.origin if (line_to_merge.origin and line.origin) else False})
        self.write({'invoice_line': [(2, x, 0) for x in to_delete]})
        
account_invoice()