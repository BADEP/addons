from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _generate_moves(self):
        for production in self:
            super(MrpProduction, self.with_context(active_model='mrp.production', active_id=production.id))._generate_moves()
        return True