from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class LaunchProcurementWizard(models.TransientModel):
    _inherit = 'launch.procurement.wizard'

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("Vous ne pouvez créer des approvisionnements pour une commande à la fois."))
        res = super(LaunchProcurementWizard, self).default_get(fields)
        if res and res.get('line_ids'):
            for line in res.get('line_ids'):
                sale_line_id = self.env['sale.order.line'].browse(line[2]['sale_order_line_id'])
                bom = self.env['mrp.bom']._bom_find(product=sale_line_id.product_id)
                if bom and bom.type == 'phantom':
                    line[2].update({'quantity_editable': False})
                else:
                    line[2].update({'quantity_editable': True})
        return res

class LaunchProcurementWizardLine(models.TransientModel):
    _inherit = 'launch.procurement.wizard.line'
    quantity_editable = fields.Boolean()
