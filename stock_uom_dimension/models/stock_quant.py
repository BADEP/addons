from odoo import models, api, fields

class StockQuant(models.Model):
    _inherit = ['stock.quant', 'uom.line']
    _name = 'stock.quant'

    def get_uom_field(self):
        return 'product_uom_id'
    def get_qty_field(self):
        return 'quantity'

    # def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
    #     quants = super()._gather(product_id, location_id, lot_id, package_id, owner_id, strict)
    #     if not self.env.context.get('dimension_ids'):
    #         return quants
    #     else:
    #         return quants.filtered(lambda q: all(d.quantity == self.env.context['dimension_ids'].get(d.dimension_id, 0) for d in q.dimension_ids))

class StockMoveDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'stock.quant.dimension'

    line_id = fields.Many2one('stock.quant', required=True, ondelete='cascade')