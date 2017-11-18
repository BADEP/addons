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

import logging
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class AutomaticWorkflowJob(models.Model):
    _inherit = 'automatic.workflow.job'

    @api.model
    def _create_invoices(self):
        immediate_pickings = self.env['stock.picking'].search(
            [('state', '=', 'done'),
             ('invoice_state', '=', '2binvoiced'),
             ('workflow_process_id.create_invoice', '=', True),
             ('workflow_process_id.create_invoice_grouped', '=', False)],
        )
        if immediate_pickings:
            _logger.debug('Pickings to invoice immediately: %s', immediate_pickings)
            ctx = self.env.context.copy()
            ctx.update({'active_ids': immediate_pickings.ids})
            vals = {}
            wizard = self.env['stock.invoice.onshipping'].with_context(ctx).create(vals)
            invoice_ids = wizard.create_invoice()
            _logger.debug('Invoices created: %s', invoice_ids)

    @api.model
    def _create_daily_invoices(self):
        invoice_pdate = fields.Date.from_string(fields.Date.today()) - relativedelta(days = 1)
        invoice_day = invoice_pdate.day
        invoice_date = fields.Date.to_string(invoice_pdate)
        
        grouped_pickings = self.env['stock.picking'].search(
            [('state', '=', 'done'),
             ('invoice_state', '=', '2binvoiced'),
             ('workflow_process_id.create_invoice', '=', True),
             ('workflow_process_id.create_invoice_grouped', '=', True),
             ('workflow_process_id.create_invoice_day', '=', invoice_day)]
        ).sorted(lambda p: p.group_id)
        groups = grouped_pickings.mapped('group_id')
        for group in groups:
            pickings = grouped_pickings.filtered(lambda p: p.group_id == group)
            if pickings:
                _logger.debug('Grouped pickings to invoice: %s', pickings)
                ctx = self.env.context.copy()
                ctx.update({'active_ids': pickings.ids})
                vals = {'group': True}
                wizard = self.env['stock.invoice.onshipping'].with_context(ctx).create(vals)
                invoice_ids = wizard.create_invoice()
                _logger.debug('Invoices created: %s', invoice_ids)
            
    @api.model
    def run(self):
        self._validate_sale_orders()
        self._validate_pickings()
        self._create_invoices()
        self._validate_invoices()
        return True
    
    @api.model
    def run_daily(self):
        self._validate_sale_orders()
        self._validate_pickings()
        self._create_invoices()
        self._create_daily_invoices()
        self._validate_invoices()
        return True
   
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    workflow_process = fields.Many2one('sale.workflow.process', string="Flux automatique")
    credit_limit_type = fields.Selection([('none', 'Aucun'),('ceiling','Plafond'),('percent','Pourcentage')], string='Type de limite de crédit', required = True, default="none")
    credit_limit_block_delivery = fields.Boolean(string='Bloquer les livraisons au delà du plafond')
    grace_delay = fields.Integer(string="Délai de grâce")
    grace_delay_block_delivery = fields.Boolean(string='Bloquer les livraisons au delà du délai de grâce')
    code_prolight = fields.Char(string='Code Prolight')
