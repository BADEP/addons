from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = ['stock.move.line', 'uom.line']
    _name = 'stock.move.line'

    dimension_ids = fields.One2many('stock.move.line.dimension', 'line_id', string='Dimensions', copy=True)
    product_dimension_qty_done = fields.Integer('Nombre fait', required=True, default=0, copy=False)

    def get_uom_field(self):
        return 'product_uom_id'
    def get_qty_field(self):
        return 'product_uom_qty'

    @api.onchange('product_uom')
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    @api.onchange('dimension_ids', 'product_dimension_qty_done')
    def onchange_dimensions(self):
        if self.dimension_ids and self.product_dimension_qty:
            self.qty_done = (self.product_dimension_qty_done * self.product_uom_qty) / self.product_dimension_qty

class StockMoveLineDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = "stock.move.line.dimension"

    line_id = fields.Many2one('stock.move.line', required=True, ondelete='cascade')
