# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    folder_id = fields.Many2one('documents.folder', ondelete="restrict", track_visibility="onchange", index=True)

    def write(self, vals):
        if vals.get('folder_id'):
            return super(IrAttachment, self.sudo()).write(vals)
        else:
            return super(IrAttachment, self).write(vals)

class DocumentFolder(models.Model):
    _name = 'documents.folder'
    _description = 'Documents Folder'
    _parent_name = 'parent_folder_id'
    _order = 'sequence'


    name = fields.Char(required=True, translate=True)
    parent_folder_id = fields.Many2one('documents.folder',
                                       string="Parent Folder",
                                       ondelete="cascade",
                                       help="Tag categories from parent folders will be shared to their sub folders")
    company_id = fields.Many2one('res.company', 'Company',
                                 help="This folder will only be available for the selected company", default=lambda self: self.env.user.company_id.id)

    sequence = fields.Integer('Sequence', default=10)
    attachment_ids = fields.One2many('ir.attachment', 'folder_id', string="Documents")
