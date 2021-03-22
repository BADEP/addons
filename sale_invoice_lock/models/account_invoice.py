from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def write(self, vals):
        for rec in self.filtered(lambda i: any(s.state == 'done' for s in i.invoice_line_ids.mapped('sale_line_ids.order_id'))):
            raise UserError('La commande relative est bloquée')
        return super().write(vals)