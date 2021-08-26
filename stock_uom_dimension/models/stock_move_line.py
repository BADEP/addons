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

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        return res.with_context(dimension_ids=vals_list.get('dimension_ids', False))

    def _free_reservation(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, ml_to_ignore=None):
        return super(StockMoveLine, self.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in self.dimension_ids},
                                                      product_dimension_qty=self.move_id.product_dimension_qty))._free_reservation(product_id, location_id,
                                                                                                           quantity, lot_id=lot_id,
                                                                                                           package_id=package_id,
                                                                                                           owner_id=owner_id,
                                                                                                           ml_to_ignore=ml_to_ignore)

    # todo: use product_dimension_qty in sstock.move.line
    @api.one
    def write(self, vals):
        return super(StockMoveLine, self.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in self.dimension_ids},
                                                      product_dimension_qty=self.move_id.product_dimension_qty)).write(vals)

    # todo: use product_dimension_qty in stock.move.line
    @api.one
    def _action_done(self):
        return super(StockMoveLine, self.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in self.dimension_ids},
                                                      product_dimension_qty=self.move_id.product_dimension_qty))._action_done()


class StockMoveLineDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = "stock.move.line.dimension"

    line_id = fields.Many2one('stock.move.line', required=True, ondelete='cascade')
