import ntpath
import os
import shutil
import tarfile
from random import randint

from openerp.exceptions import ValidationError
from openerp import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class Attachments(models.Model):
    _inherit = "ir.attachment"

    active = fields.Boolean('Active?', default=True)


class download_attachments(models.TransientModel):
    _name = 'download.attachments'

    attachment = fields.Binary('Attachement', readonly=True)
    filename = fields.Char('File Name')
    active_model = fields.Char('Active Model')
    active_id = fields.Char('Active ID')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.model
    def default_get(self, fields):
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_id and active_model:
            try:
                fname = self.env[active_model].browse(active_id).name
            except ValueError:
                pass
            if not fname:
                fname = 'odoo'
        res = super(download_attachments, self).default_get(fields)
        return res

    @api.multi
    def download_attachments(self):
        config_obj = self.env['ir.config_parameter']
        attachment_obj = self.env['ir.attachment']

        active_ids = self._context.get('active_ids')
        attachment_ids = active_ids
        ids = self._ids
        filestore_path = os.path.join(attachment_obj._filestore(), '')
        attachment_dir = filestore_path + 'attachments'
        # create directory and remove its content
        if not os.path.exists(attachment_dir):
            os.makedirs(attachment_dir)
        else:
            shutil.rmtree(attachment_dir)
            os.makedirs(attachment_dir)
        file_name = 'attachments'
        if isinstance(ids, int):
            ids = [ids]
        wzrd_obj = self
        config_ids = config_obj.search([('key', '=', 'web.base.url')])
        self.env['ir.attachment'].search([('active','=',False)]).unlink()


        if len(config_ids):
            value = config_ids[0].value
            active_model = 'ir.attachment'  # wzrd_obj.active_model
            active_id = wzrd_obj.id
            # tar_dir = attachment_dir + '/' + file_name
            tar_dir = os.path.join(attachment_dir, file_name)
            tFile = tarfile.open(tar_dir, 'w:gz')
            if value and active_id and active_model:
                # change working directory otherwise file is tared with all its parent directories
                original_dir = os.getcwd()
                filter_attachments = []
                for attach in attachment_obj.browse(attachment_ids):
                    if attach.active:
                        filter_attachments.append(attach.id)
                if not filter_attachments:
                    raise ValidationError(_("No attachment to download"))
                for attachment in attachment_obj.browse(filter_attachments):
                    # to get full path of file
                    full_path = attachment_obj._full_path(attachment.store_fname)
                    attachment_name = attachment.datas_fname
                    new_file = os.path.join(attachment_dir, attachment_name)
                    # copying in a new directory with a new name
                    # shutil.copyfile(full_path, new_file)
                    try:
                        shutil.copy2(full_path, new_file)
                    except:
                        pass
                        #raise UserError(_("Not Proper file name to download"))
                    head, tail = ntpath.split(new_file)
                    # change working directory otherwise it tars all parent directory
                    os.chdir(head)
                    try:
                        tFile.add(tail)
                    except:
                        _logger.error("No such file was found : %s" %tail)
                tFile.close()
                os.chdir(original_dir)
                values = {
                    'name': file_name + '.tar.gz',
                    'datas_fname': file_name + '.tar.gz',
                    'res_model': 'download.attachments',
                    'res_id': ids[0],
                    'res_name': 'test....',
                    'type': 'binary',
                    'store_fname': 'attachments/attachments',
                    'active' : False,
                }
                attachment_id = self.env['ir.attachment'].create(values)
                url = "%s/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=%s" % (value, attachment_id.id)
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'nodestroy': False,
                }
