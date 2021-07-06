from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line', 'uom.line']
    _name = 'purchase.order.line'

    dimension_ids = fields.One2many('purchase.order.line.dimension', 'line_id', string='Dimensions', copy=True)

    def get_uom_field(self):
        return 'product_uom'
    def get_qty_field(self):
        return 'product_qty'

    @api.onchange('product_uom')
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        values = super()._prepare_stock_moves(picking)
        values[0].update({
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in
                              self.dimension_ids],
            'product_dimension_qty': self.product_dimension_qty
        })
        return values

    def _prepare_account_move_line(self, move):
        values = super()._prepare_account_move_line(move)
        values.update({
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in
                              self.dimension_ids],
            'product_dimension_qty': self.product_dimension_qty
        })
        return values


class purchaseOrderLineDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'purchase.order.line.dimension'

    line_id = fields.Many2one('purchase.order.line', required=True, ondelete='cascade')