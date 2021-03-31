

from odoo.models import api, Model
from odoo.tools.safe_eval import const_eval


class IrConfigParameter(Model):
    _inherit = "ir.config_parameter"

    @api.model
    def get_attachment_config(self):
        get_param = self.sudo().get_param
        return {
            'optimize_pdf': get_param("base_attachment_optimize.optimize_pdf", False),
            'optimize_images': get_param("base_attachment_optimize.optimize_images", False),
            'pdf_quality': const_eval(get_param("base_attachment_optimize.pdf_quality", 'ebook')),
            'dpi_quality': get_param("base_attachment_optimize.dpi_quality", 300),
            'jpeg_quality': get_param("base_attachment_optimize.jpeg_quality", 80),
            'batch_size': get_param("base_attachment_optimize.batch_size", 100)
        }
