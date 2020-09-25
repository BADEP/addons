from odoo import fields, models
from odoo.tools import float_compare

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _update_received_qty(self):
        super(PurchaseOrderLine, self)._update_received_qty()
        for line in self.filtered(lambda x: x.move_ids and x.product_id.id not in x.move_ids.mapped('product_id').ids):
            bom = self.env['mrp.bom']._bom_find(product=line.product_id, company_id=line.company_id.id)
            if bom and bom.type_purchase == 'phantom':
                line.qty_received = line._get_bom_delivered(bom=bom)

class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_explode(self):
        """ Explodes pickings """
        # in order to explode a move, we must have a picking_type_id on that move because otherwise the move
        # won't be assigned to a picking and it would be weird to explode a move into several if they aren't
        # all grouped in the same picking.
        if not self.picking_type_id:
            return self
        bom = self.env['mrp.bom'].sudo()._bom_find(product=self.product_id, company_id=self.company_id.id)
        if not bom or (bom.type_purchase != 'phantom' and bom.type != 'phantom'):
            return self
        phantom_moves = self.env['stock.move']
        processed_moves = self.env['stock.move']
        factor = self.product_uom._compute_quantity(self.product_uom_qty, bom.product_uom_id) / bom.product_qty
        boms, lines = bom.sudo().explode(self.product_id, factor, picking_type=bom.picking_type_id)
        for bom_line, line_data in lines:
            phantom_moves += self._generate_move_phantom(bom_line, line_data['qty'])

        for new_move in phantom_moves:
            processed_moves |= new_move.action_explode()
        #         if not self.split_from and self.procurement_id:
        #             # Check if procurements have been made to wait for
        #             moves = self.procurement_id.move_ids
        #             if len(moves) == 1:
        #                 self.procurement_id.write({'state': 'done'})
        if processed_moves and self.state == 'assigned':
            # Set the state of resulting moves according to 'assigned' as the original move is assigned
            processed_moves.write({'state': 'assigned'})
        # delete the move with original product which is not relevant anymore
        self.sudo().unlink()
        return processed_moves