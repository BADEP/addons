# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    Ported to new API by Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp import models, api, _, workflow, exceptions


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def has_valuation_moves(self):
        self.ensure_one()
        account_moves = self.env['account.move'].search(
            [('ref', '=', self.name)])
        return bool(account_moves)

    @api.multi
    def action_revert_done(self):
        for picking in self:
            if picking.has_valuation_moves():
                raise exceptions.Warning(
                    _('Picking %s has valuation moves: '
                        'remove them first.')
                    % (picking.name))
            if picking.invoice_id:
                raise exceptions.Warning(
                    _('Picking %s has invoices!') % (picking.name))
            for move in picking.move_lines:
                for quant in move.quant_ids:
                    if move.location_id.id == quant.location_id.id:
                        quant.qty += move.product_uom_qty
                    elif move.location_dest_id.id == quant.location_id.id:
                        quant.qty -= move.product_uom_qty
                move.procurement_id.write({'state': 'exception'})
            picking.move_lines.write({'state': 'draft'})
            picking.pack_operation_ids.unlink()
            picking.state = 'draft'
            if picking.invoice_state == 'invoiced' and not picking.invoice_id:
                picking.invoice_state = '2binvoiced'
            # Deleting the existing instance of workflow
            workflow.trg_delete(
                self._uid, 'stock.picking', picking.id, self._cr)
            workflow.trg_create(
                self._uid, 'stock.picking', picking.id, self._cr)
            picking.message_post(
                _("The picking has been re-opened and set to draft state"))
            if picking.sale_id:
                picking.sale_id.write({'state': 'progress'})
                instance = self.env['workflow.instance'].search([('res_type','=','sale.order'),('res_id','=',picking.sale_id.id)])
                instance.state = 'active'
                for item in self.env['workflow.workitem'].search([('inst_id','=',instance.id)]):
                    item.state = 'active'
        return
