from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_confirm(self, merge=True, merge_into=False):
        production_moves = self.filtered(lambda m: m.production_id).with_context(force_no_merge=True)
        raw_moves = self.filtered(lambda m: not m.production_id).with_context(force_no_merge=False)
        moves1 = super(StockMove, production_moves)._action_confirm(merge=merge, merge_into=merge_into)
        moves2 = super(StockMove, raw_moves)._action_confirm(merge=merge, merge_into=merge_into)
        return (moves1 | moves2)

    def _merge_moves(self, merge_into=False):
        if self.env.context.get('force_no_merge'):
            return self
        else:
            return super()._merge_moves(merge_into=merge_into)
