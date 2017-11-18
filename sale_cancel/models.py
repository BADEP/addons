# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    def action_cancel(self):
        for invoice in self.invoice_ids:
            if invoice.move_id:
                for move_line in invoice.move_id.line_id:
                    move_line.reconcile_id.unlink()
                    move_line.reconcile_partial_id.unlink()
            invoice.sudo().actiorn_cancel()
            invoice.internal_number = ''
            invoice.unlink()
        for picking in self.picking_ids:
            picking.sudo().action_revert_done()
            picking.unlink()
        res = super(SaleOrder, self).action_cancel()
        return res