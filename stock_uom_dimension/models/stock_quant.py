from odoo import models, api, fields


class StockQuant(models.Model):
    _inherit = ['stock.quant', 'uom.line']
    _name = 'stock.quant'

    dimension_ids = fields.One2many('stock.quant.dimension', 'line_id', string='Dimensions', copy=True)

    def get_uom_field(self):
        return 'product_uom_id'

    def get_qty_field(self):
        return 'quantity'

    @api.model
    def create(self, vals):
        if self.env.context.get('dimension_ids', False):
            vals.update({
                'product_dimension_qty': self.env.context.get('product_dimension_qty'),
                'dimension_ids': [(0, 0, {'dimension_id': k, 'quantity': v}) for k, v in self.env.context.get('dimension_ids').items()]
            })
        return super().create(vals)

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        quants = super(StockQuant, self)._gather(product_id, location_id, lot_id, package_id, owner_id, strict)
        if self.env.context.get('dimension_ids') and product_id.stock_dimensions_strict:
            return quants.filtered(lambda q: q.dimension_ids.mapped('dimension_id').ids == list(self.env.context.get('dimension_ids').keys()) and
                                             all(d.quantity == self.env.context['dimension_ids'].get(d.dimension_id.id, 0) for d in q.dimension_ids))
        return quants


class StockMoveDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'stock.quant.dimension'

    line_id = fields.Many2one('stock.quant', required=True, ondelete='cascade')
