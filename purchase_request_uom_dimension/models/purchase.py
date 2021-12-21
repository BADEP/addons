from odoo import models, fields, api

class PurchaseRequestLine(models.Model):
    _inherit = ['purchase.request.line', 'uom.line']
    _name = 'purchase.request.line'

    _uom_field = 'product_uom_id'
    _qty_field = 'product_qty'

    dimension_ids = fields.One2many('purchase.order.line.dimension', 'line_id', string='Dimensions', copy=True)

    @api.depends(_qty_field)
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.onchange(_uom_field)
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        values = super()._prepare_stock_moves(picking)
        if values:
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