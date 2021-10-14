from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = ['stock.move', 'uom.line']
    _name = 'stock.move'

    dimension_ids = fields.One2many('stock.move.dimension', 'line_id', string='Dimensions', copy=True)
    product_dimension_qty_done = fields.Integer('Nombre fait', required=True, default=0, copy=False)

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('dimension_ids')
        return distinct_fields

    def get_uom_field(self):
        return 'product_uom'

    def get_qty_field(self):
        return 'product_uom_qty'

    @api.onchange('product_uom')
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    @api.onchange('dimension_ids', 'product_dimension_qty_done')
    def onchange_dimensions(self):
        if self.dimension_ids and self.product_dimension_qty > 0:
            self.quantity_done = (self.product_dimension_qty_done * self.product_uom_qty) / self.product_dimension_qty
        elif self.dimension_ids and self.product_dimension_qty == 0:
            self.quantity_done = 0

    @api.one
    def write(self, vals):
        res = super().write(vals)
        if vals.get('product_dimension_qty'):
            self.onchange_dimensions()

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res.update({
            'product_dimension_qty': self.product_dimension_qty - self.product_dimension_qty_done,
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in self.dimension_ids]
        })
        return res

    def _split(self, qty, restrict_partner_id=False):
        new_move = self.browse(super()._split(qty, restrict_partner_id))
        new_move.write({'product_dimension_qty': self.product_dimension_qty - self.product_dimension_qty_done})
        self.with_context(do_not_propagate=True, do_not_unreserve=True, rounding_method='HALF-UP').write({'product_dimension_qty': self.product_dimension_qty_done})
        return new_move.id

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
