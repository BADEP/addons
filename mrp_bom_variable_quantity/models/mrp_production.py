from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _generate_moves(self):
        return super(MrpProduction, self.with_context(production_id=self))._generate_moves()

    def _get_moves_raw_values(self):
        return super(MrpProduction, self.with_context(production_id=self))._get_moves_raw_values()

    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
        res = super()._get_move_raw_values(product_id, product_uom_qty, product_uom, operation_id, bom_line)
        if bom_line and bom_line.qty_type == 'variable':
            factor = self.product_uom_id._compute_quantity(self.product_qty, self.bom_id.product_uom_id) / self.bom_id.product_qty
            eval_context = {
                'env': self.env,
                'context': self.env.context,
                'user': self.env.user,
                'production_id': self,
                'line': bom_line,
                'quantity': factor
            }
            line_extra_data = bom_line.qty_formula_id.execute_extra_data(eval_context)
            if isinstance(line_extra_data, dict):
                res.update(line_extra_data)
        return res


    #Force move raw recalculation since formulas are not linear
    #Todo: compare _update_raw_moves and _onchange_move_raw and add diff as new raw moves
    # def _update_raw_moves(self, factor):
    #     self.ensure_one()
    #     self._onchange_move_raw()
    #     return []