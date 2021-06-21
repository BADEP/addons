from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = ['stock.move', 'uom.line']
    _name = 'stock.move'

    dimension_ids = fields.One2many('stock.move.dimension', 'line_id', string='Dimensions', copy=True)
    product_dimension_qty_done = fields.Integer('Nombre fait', required=True, default=0, copy=False)

    def get_uom_field(self):
        return 'product_uom'

    def get_qty_field(self):
        return 'product_uom_qty'

    @api.onchange('product_uom')
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    @api.onchange('dimension_ids', 'product_dimension_qty_done')
    def onchange_dimensions(self):
        if self.dimension_ids and self.product_dimension_qty:
            self.quantity_done = (self.product_dimension_qty_done * self.product_uom_qty) / self.product_dimension_qty

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res.update({
            'product_dimension_qty': self.product_dimension_qty,
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in self.dimension_ids]
        })
        return res

    @api.one
    def _action_assign(self):
        return super(StockMove, self.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in self.dimension_ids},
                                                  product_dimension_qty=self.product_dimension_qty))._action_assign()

    @api.one
    @api.depends('state', 'product_id', 'product_qty', 'location_id')
    def _compute_product_availability(self):
        return super(StockMove, self.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in self.dimension_ids},
                                                  product_dimension_qty=self.product_dimension_qty))._compute_product_availability()

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        vals.update({
            'product_dimension_qty': self.product_dimension_qty,
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in self.dimension_ids]
        })
        return vals


class StockMoveDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = "stock.move.dimension"

    line_id = fields.Many2one('stock.move', required=True, ondelete='cascade', oldname='stock_move_id')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['dimension_ids', 'product_dimension_qty']
        return fields
