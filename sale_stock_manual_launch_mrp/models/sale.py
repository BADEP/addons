from odoo import models, api, fields
from odoo.addons import decimal_precision as dp

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    procurement_qty_manual = fields.Float(string="Qté lancée", digits='Product Unit of Measure', store=False)

    def get_dummy_qty(self):
        self.ensure_one()
        return self.product_uom_qty - self.procurement_qty

    def action_launch_procurement(self):
        bom = self.env['mrp.bom']._bom_find(product=self.product_id)
        if bom and bom.type == 'phantom' and self.env.context.get('qty_to_launch'):
            self.procurement_qty_manual = self.env.context['qty_to_launch']
        return super().action_launch_procurement()

    def _get_procurement_quantity(self):
        for rec in self:
            bom = self.env['mrp.bom']._bom_find(product=rec.product_id)
            if bom and bom.type == 'phantom':
                moves = rec.move_ids.filtered(lambda m: m.picking_id and m.state != 'cancel')
                outgoing_moves = moves.filtered(lambda m: m.location_dest_id.usage == "customer" and (
                            not m.origin_returned_move_id or (m.origin_returned_move_id and m.to_refund)))
                if outgoing_moves:
                    rec.procurement_qty = rec.procurement_qty_manual - self.env.context.get('qty_to_launch', 0)
            else:
                super(SaleOrderLine, rec)._get_procurement_quantity()
