# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    optimize_pdf = fields.Boolean('Optimize PDF Files', config_parameter='base_attachment_optimize.optimize_pdf')
    optimize_images = fields.Boolean('Optimize Images', config_parameter='base_attachment_optimize.optimize_images')
    pdf_quality = fields.Selection([('screen','screen'),('ebook','ebook'),('prepress','prepress'),('print','print'),('default','default')], string='PDF Quality', config_parameter='base_attachment_optimize.pdf_quality', default='ebook')
    dpi_quality = fields.Integer('PNG Quality', config_parameter='base_attachment_optimize.png_quality', default=300)
    jpeg_quality = fields.Integer('JPEG Quality', config_parameter='base_attachment_optimize.jpeg_quality', default=80)
    batch_size = fields.Integer('Batch size', config_parameter='base_attachment_optimize.batch_size', default=100)
