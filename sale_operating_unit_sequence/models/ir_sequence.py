# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    operating_unit_id = fields.Many2one('operating.unit')

    @api.model
    def next_by_code(self, sequence_code):
        """ Draw an interpolated string using a sequence with the requested code.
            If several sequences with the correct code are available to the user
            (multi-company cases), the one from the user's current company will
            be used.

            :param dict context: context dictionary may contain a
                ``force_company`` key with the ID of the company to
                use instead of the user's current company for the
                sequence selection. A matching sequence for that
                specific company will get higher priority.
        """
        self.check_access_rights('read')
        operating_unit_id = self._context.get('operating_unit_id')
        if operating_unit_id:
            force_company = self._context.get('force_company')
            if not force_company:
                force_company = self.env.user.company_id.id
            seq_ids = self.search(
                [('code', '=', sequence_code), ('operating_unit_id', 'in', [operating_unit_id, False]),
                 ('company_id', 'in', [force_company, False])], order='operating_unit_id,company_id')
            if not seq_ids:
                _logger.debug(
                    "No ir.sequence has been found for code '%s'. Please make sure a sequence is set for current operating unit." % sequence_code)
                return False
            seq_id = seq_ids[0]
            return seq_id._next()
        else:
            return super().next_by_code(sequence_code)
