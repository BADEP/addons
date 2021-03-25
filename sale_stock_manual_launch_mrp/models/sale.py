from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    procurement_qty = fields.Float(string="Qté lancée", compute='_get_procurement_quantity', digits=dp.get_precision('Product Unit of Measure'))
    to_launch = fields.Boolean(string="To Launch Procurement", compute='_get_to_launch')

    @api.one
    def get_dummy_qty(self):
        return self.product_uom_qty - self.procurement_qty

    @api.depends('product_uom_qty')
    def _get_procurement_quantity(self):
        for rec in self:
            bom = self.env['mrp.bom']._bom_find(product=rec.product_id)
            if bom and bom.type == 'phantom':
                moves = rec.move_ids.filtered(lambda m: m.picking_id and m.state != 'cancel')
                outgoing_moves = moves.filtered(lambda m: m.location_dest_id.usage == "customer" and (
                            not m.origin_returned_move_id or (m.origin_returned_move_id and m.to_refund)))
                if outgoing_moves:
                    rec.procurement_qty = rec.qty_delivered_manual or rec.product_uom_qty
            else:
                rec.procurement_qty = super(SaleOrderLine, rec.with_context(previous_product_uom_qty={rec.id: 0}))._get_qty_procurement()
