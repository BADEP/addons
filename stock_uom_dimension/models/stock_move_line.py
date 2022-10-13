from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = ['stock.move.line', 'uom.line']
    _name = 'stock.move.line'

    _uom_field = 'product_uom_id'
    _qty_field = 'product_uom_qty'

    dimension_ids = fields.One2many('stock.move.line.dimension', 'line_id', string='Dimensions', copy=True)
    product_dimension_qty_done = fields.Integer('Nombre fait', required=True, default=0, copy=False)

    @api.depends(_qty_field)
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.onchange(_uom_field)
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    @api.onchange('dimension_ids', 'product_dimension_qty_done')
    def onchange_dimensions(self):
        if self.dimension_ids and self.product_dimension_qty_done:
            self.qty_done = self.product_uom_id.eval_values(dict([(d.dimension_id.id, d.quantity) for d in self.dimension_ids]),
                                                            self.product_dimension_qty_done)

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        return res.with_context(dimension_ids=vals_list.get('dimension_ids', False))

    def _free_reservation(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, ml_to_ignore=None):
        return super(StockMoveLine, self.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in self.dimension_ids}))._free_reservation(
            product_id,
            location_id,
            quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            ml_to_ignore=ml_to_ignore
        )

    def write(self, vals):
        res = True
        for rec in self:
            res = res and super(StockMoveLine, rec.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in rec.dimension_ids})).write(vals)
        return res

    def _action_done(self):
        dim_list = []
        for rec in self:
            dim_dict = {d.dimension_id.id: d.quantity for d in rec.dimension_ids}
            if dim_dict not in dim_list:
                dim_list.append(dim_dict)
        for dim_dict in dim_list:
            recs = self.filtered(lambda rec: rec.exists())
            recs = recs.filtered(lambda rec: dim_dict == {d.dimension_id.id: d.quantity for d in rec.dimension_ids})
            super(StockMoveLine, recs.with_context(dimension_ids=dim_dict))._action_done()

class StockMoveLineDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = "stock.move.line.dimension"

    line_id = fields.Many2one('stock.move.line', required=True, ondelete='cascade')
