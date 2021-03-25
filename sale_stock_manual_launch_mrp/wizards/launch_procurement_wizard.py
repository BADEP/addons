from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class LaunchProcurementWizardLine(models.TransientModel):
    _inherit = 'launch.procurement.wizard.line'
    quantity_editable = fields.Boolean(compute='get_quantity_editable')

    @api.depends('quantity')
    def get_quantity_editable(self):
        for rec in self:
            bom = self.env['mrp.bom']._bom_find(product=rec.sale_order_line_id.product_id)
            if bom and bom.type == 'phantom':
                rec.quantity_editable = False
            else:
                rec.quantity_editable = True
