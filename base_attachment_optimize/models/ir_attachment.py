# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
#import ghostscript
import base64
import locale
import os


from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):

    _inherit = 'ir.attachment'

    optimized = fields.Boolean('Optimized', default=False, readonly=True, store=True)

    def optimize(self):
        pdfquality = self.env['ir.config_parameter'].sudo().get_param('base_attachment_optimize.pdf_quality')
        for att in self:
            try:
                path = att._full_path(att.store_fname)
                cmd = "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/%s -dNOPAUSE -dQUIET -dBATCH -sOutputFile=/tmp/%s %s" % (pdfquality, att.checksum, path)
                os.system(cmd)
                # args = [
                #     "-dNOPAUSE", "-dBATCH", "-dQUIET",
                #     "-sDEVICE=pdfwrite",
                #     '-dCompatibilityLevel=1.5',
                #     "-dPDFSETTINGS=/" + pdfquality,
                #     "-sOutputFile=/tmp/output.pdf",
                #     "-f", path
                # ]
                # encoding = locale.getpreferredencoding()
                # args = [a.encode(encoding) for a in args]
                # ghostscript.Ghostscript(*args)
                bin_datas = open('/tmp/%s' % att.checksum, 'rb').read()
                if att.file_size > len(bin_datas):
                    att.write({'datas': base64.b64encode(bin_datas)})
                    os.system("rm %" % path)
            except Exception:
                pass
        self.write({'optimized': True})

    @api.model
    def cron_compress(self):
        if self.env['ir.config_parameter'].sudo().get_param('base_attachment_optimize.optimize_pdf'):
            attachments = self.search([('mimetype', '=', 'application/pdf'), ('type', '=', 'binary'), ('optimized', '=', False)],
                                       limit=int(self.env['ir.config_parameter'].sudo().get_param('base_attachment_optimize.batch_size')))
            attachments.optimize()
        return True

    def _inverse_datas(self):
        super(IrAttachment, self)._inverse_datas()
        self.write({'optimized': False})
