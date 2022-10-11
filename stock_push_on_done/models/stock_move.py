# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=lambda self: self.env.context.get('cancel_backorder')):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for rec in self:
            rec.location_dest_id = rec.move_line_ids[0].location_dest_id if len(rec.mapped('move_line_ids.location_dest_id')) == 1 else rec.location_dest_id
        self._push_apply()
        return res