from odoo import models, fields, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def write(self, vals):
        for rec in self.filtered(lambda i: i.sale_id and i.sale_id.state == 'done'):
            raise UserError('Le transfert est bloquée par la commande ' + rec.sale_id.name)
        return super().write(vals)
