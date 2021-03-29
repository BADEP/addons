from odoo import models, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    def get_dummy_qty(self):
        return self.product_uom_qty - self.procurement_qty

    def _get_procurement_quantity(self):
        for rec in self:
            bom = self.env['mrp.bom']._bom_find(product=rec.product_id)
            if bom and bom.type == 'phantom':
                moves = rec.move_ids.filtered(lambda m: m.picking_id and m.state != 'cancel')
                outgoing_moves = moves.filtered(lambda m: m.location_dest_id.usage == "customer" and (
                            not m.origin_returned_move_id or (m.origin_returned_move_id and m.to_refund)))
                if outgoing_moves:
                    rec.procurement_qty = (rec.qty_delivered_manual or rec.product_uom_qty) - self.env.context.get('qty_to_launch', 0)
            else:
                super(SaleOrderLine, rec)._get_procurement_quantity()
