from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

class LaunchProcurementWizard(models.TransientModel):
    _inherit = 'launch.procurement.wizard'
    _description = 'Launch procurement wizard'

    def launch_procurement(self):
        for line in self.line_ids.filtered(lambda l: not l.sale_order_line_id.dimension_ids):
            line.sale_order_line_id.with_context(qty_to_launch=line.quantity).action_launch_procurement()
        for line in self.line_ids.filtered(lambda l: l.sale_order_line_id.dimension_ids):
            line.sale_order_line_id.with_context(qty_to_launch=line.sale_order_line_id.product_uom.eval_values(
                dict([(d.dimension_id.id, d.quantity) for d in line.sale_order_line_id.dimension_ids]), line.quantity)).action_launch_procurement()

class launch_measures_wizard_line(models.TransientModel):
    _inherit = 'launch.procurement.wizard.line'

    @api.constrains('quantity')
    def _check_max_qty(self):
        for rec in self.filtered(lambda l: l.sale_order_line_id.dimension_ids):
            if float_compare(rec.quantity, rec.sale_order_line_id.product_dimension_qty * (rec.sale_order_line_id.measured_quantity - rec.sale_order_line_id.procurement_qty) / rec.sale_order_line_id.product_uom_qty, 3) > 0:
                raise ValidationError("Vous ne pouvez pas lancer en approvisionnement plus que la quantité restante: %s" % (
                        str((rec.sale_order_line_id.measured_quantity - rec.sale_order_line_id.procurement_qty)/rec.sale_order_line_id.product_uom_qty)))
        super(launch_measures_wizard_line, self.filtered(lambda l: not l.sale_order_line_id.dimension_ids))._check_max_qty()
