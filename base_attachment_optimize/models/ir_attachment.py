# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import hashlib
import itertools
import logging
import mimetypes
import os
import io
import re
from collections import defaultdict
import uuid

from odoo import api, fields, models, tools, SUPERUSER_ID, exceptions, _
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import config, human_size, ustr, html_escape
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import crop_image, image_resize_image
from PyPDF2 import PdfFileWriter, PdfFileReader

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):

    _inherit = 'ir.attachment'

    @api.model
    def _file_write(self, value, checksum):
        bin_value = base64.b64decode(value)
        fname, full_path = self._get_path(bin_value, checksum)
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
                # add fname to checklist, in case the transaction aborts
                self._mark_for_gc(fname)
            except IOError:
                _logger.info("_file_write writing %s", full_path, exc_info=True)
        return fname

    def _inverse_datas(self):
        location = self._storage()
        for attach in self:
            # compute the fields that depend on datas
            value = attach.datas
            bin_data = base64.b64decode(value) if value else b''
            vals = {
                'file_size': len(bin_data),
                'checksum': self._compute_checksum(bin_data),
                'index_content': self._index(bin_data, attach.datas_fname, attach.mimetype),
                'store_fname': False,
                'db_datas': value,
            }
            if value and location != 'db':
                # save it to the filestore
                vals['store_fname'] = self._file_write(value, vals['checksum'])
                vals['db_datas'] = False

            # take current location in filestore to possibly garbage-collect it
            fname = attach.store_fname
            # write as superuser, as user probably does not have write access
            super(IrAttachment, attach.sudo()).write(vals)
            if fname:
                self._file_delete(fname)
