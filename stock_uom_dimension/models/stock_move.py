from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = ['stock.move', 'uom.line']
    _name = 'stock.move'

    _uom_field = 'product_uom'
    _qty_field = 'product_uom_qty'

    dimension_ids = fields.One2many('stock.move.dimension', 'line_id', string='Dimensions', copy=True)
    product_dimension_qty_done = fields.Float('Nombre fait', required=True, default=0, copy=False)

    @api.depends(_qty_field)
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.onchange(_uom_field)
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    @api.onchange('dimension_ids', 'product_dimension_qty_done')
    def onchange_dimensions(self):
        if self.dimension_ids and self.product_dimension_qty_done:
            self.quantity_done = self._compute_dimension_qty(force_qty=self.product_dimension_qty_done)

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res.update({
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in self.dimension_ids]
        })
        return res

    def _action_assign(self):
        for rec in self:
            if rec.dimension_ids and not self.env.context.get('dimension_ids'):
                super(StockMove, rec.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in rec.dimension_ids}))._action_assign()
            else:
                super()._action_assign()

    @api.depends('state', 'product_id', 'product_qty', 'location_id')
    def _compute_product_availability(self):
        for rec in self:
            super(StockMove,
                  rec.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in rec.dimension_ids}))._compute_product_availability()

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        vals.update({
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in self.dimension_ids]
        })
        return vals


class StockMoveDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = "stock.move.dimension"

    line_id = fields.Many2one('stock.move', required=True, ondelete='cascade')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['dimension_ids']
        return fields
