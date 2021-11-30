from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_assign(self):
        for rec in self:
            if not rec.dimension_ids and rec.raw_material_production_id and rec.raw_material_production_id.dimension_ids:
                super(StockMove, rec.with_context(dimension_ids={d.dimension_id.id: d.quantity for d in rec.raw_material_production_id.dimension_ids},
                                                  product_dimension_qty=rec.raw_material_production_id.product_dimension_qty))._action_assign()
            else:
                super()._action_assign()
