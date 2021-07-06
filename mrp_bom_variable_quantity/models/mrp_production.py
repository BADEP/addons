from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _generate_moves(self):
        for production in self:
            super(MrpProduction, self.with_context(active_model='mrp.production', active_id=production.id))._generate_moves()
        return True

    #Force move raw recalculation since formulas are not linear
    #Todo: compare _update_raw_moves and _onchange_move_raw and add diff as new raw moves
    # def _update_raw_moves(self, factor):
    #     self.ensure_one()
    #     self._onchange_move_raw()
    #     return []