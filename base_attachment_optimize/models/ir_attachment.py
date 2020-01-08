# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import ghostscript
import locale

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):

    _inherit = 'ir.attachment'

    optimized = fields.Boolean('Optimized', default=False, readonly=True, store=True)

    @api.model
    def cron_compress(self):
        if self.env['ir.config_parameter'].sudo().get_param('base_attachment_optimize.optimize_pdf'):
            attachments = self.search([('mimetype', '=', 'application/pdf'), ('type', '=', 'binary'), ('optimized', '=', False)],
                                       limit=int(self.env['ir.config_parameter'].sudo().get_param('base_attachment_optimize.batch_size')))
            pdfquality = self.env['ir.config_parameter'].sudo().get_param('base_attachment_optimize.pdf_quality')
            for att in attachments:
                path = att._full_path(att.store_fname)
                args = [
                    "ps2pdf",  # actual value doesn't matter
                    "-dNOPAUSE", "-dBATCH", "-dQUIET",
                    "-sDEVICE=pdfwrite",
                    "-dPDFSETTINGS=/" + pdfquality,
                    "-sOutputFile=" + path,
                    "-f", path
                ]
                encoding = locale.getpreferredencoding()
                args = [a.encode(encoding) for a in args]
                ghostscript.Ghostscript(*args)
            attachments.write({'optimized': True})

        return True