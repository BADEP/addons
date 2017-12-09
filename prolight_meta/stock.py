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
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from itertools import groupby
import time

def grouplines(self, ordered_lines, sortkey):
    """Return lines from a specified invoice or sale order grouped by category"""
    grouped_lines = []
    for key, valuesiter in groupby(ordered_lines, sortkey):
        group = {}
        group['category'] = key
        group['lines'] = list(v for v in valuesiter)

        if 'subtotal' in key and key.subtotal is True:
            group['subtotal'] = sum((line.reserved_availability if line.picking_id.state == 'partially_available' else line.product_uom_qty) for line in group['lines'])
        grouped_lines.append(group)

    return grouped_lines

class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    @api.cr_uid_id_context
    def _name_get(self, cr, uid, location, context=None):
        name = location.name
        return name

    @api.cr_uid_ids_context
    def _complete_name(self, cr, uid, ids, name, args, context=None):
        """ Forms complete name of location from parent location to child location.
        @return: Dictionary of values
        """
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            res[m.id] = m.name
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    ignore_restrictions = fields.Boolean(default=False, string='Ignorer les restrictions')
    
    @api.multi
    def do_transfer(self):
        for picking in self:
            if picking.picking_type_id.apply_restrictions and not picking.ignore_restrictions:
                partner = picking.partner_id.parent_id and picking.partner_id.parent_id or picking.partner_id
                if partner.credit_limit_type == 'ceiling' \
                and partner.credit_limit_block_delivery \
                and partner.credit + picking.amount_total > partner.credit_limit:
                    raise except_orm('Plafond','Ce client a dépassé son plafond autorisé')
                if partner.payment_earliest_due_date:
                    if partner.grace_delay_block_delivery \
                    and time.mktime(time.localtime()) > (time.mktime(time.strptime(partner.payment_earliest_due_date, "%Y-%m-%d")) + partner.grace_delay*86400):
                        raise except_orm('Délai de grâce dépassé','Ce client a des factures échues dépassant le délai de grâce lui étant octroyé')
        res = super(StockPicking, self).do_transfer()
        ctx = self.env.context.copy()
        for picking in self:
            if picking.invoice_state == '2binvoiced' and picking.workflow_process_id.create_invoice and picking.workflow_process_id.create_invoice_grouped == False:
                ctx.update({'active_ids': picking.ids})
                vals = {}
                wizard = self.env['stock.invoice.onshipping'].with_context(ctx).create(vals)
                invoice_ids = wizard.create_invoice()
                self.env['account.invoice'].browse(invoice_ids).signal_workflow('invoice_open')
        return res

    def picking_layout_lines(self, cr, uid, ids, picking_id=None, context=None):
        """
        Returns order lines from a specified sale ordered by
        sale_layout_category sequence. Used in sale_layout module.

        :Parameters:
            -'order_id' (int): specify the concerned sale order.
        """
        move_lines = self.browse(cr, uid, picking_id, context=context).move_lines
        sortkey = lambda x: x.sale_layout_cat_id if x.sale_layout_cat_id else ''

        return grouplines(self, move_lines, sortkey)

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'
    sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section')
    categ_sequence = fields.Integer(related = 'sale_layout_cat_id.sequence', string='Sequence', store=True)

    @api.model
    def _prepare_mo_vals(self, procurement):
        res = super(ProcurementOrder, self)._prepare_mo_vals(procurement)
        res['sale_layout_cat_id'] = procurement.sale_layout_cat_id.id
        res['categ_sequence'] = procurement.categ_sequence
        return res

    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)
        res['sale_layout_cat_id'] = procurement.sale_layout_cat_id.id
        res['categ_sequence'] = procurement.categ_sequence
        return res

class StockMove(models.Model):
    _inherit = 'stock.move'
    sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section')
    categ_sequence = fields.Integer(related = 'sale_layout_cat_id.sequence', string='Sequence', store=True)

    _order = 'picking_id, categ_sequence, sale_layout_cat_id, id'

    @api.model
    def _prepare_procurement_from_move(self, move):
        res = super(StockMove, self)._prepare_procurement_from_move(move)
        res['sale_layout_cat_id'] = move.sale_layout_cat_id.id
        res['categ_sequence'] = move.categ_sequence
        return res
    
    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self)._get_invoice_line_vals(move, partner, inv_type)
        res['sale_layout_cat_id'] = move.sale_layout_cat_id.id
        res['categ_sequence'] = move.categ_sequence
        return res

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    apply_restrictions = fields.Boolean(string='Appliquer les restrictions sur le partenaire')