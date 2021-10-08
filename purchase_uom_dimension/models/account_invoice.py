from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        values = super()._prepare_invoice_line_from_po_line(line)
        #TODO: fix me
        # values.update({
        #     'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in
        #                       line.dimension_ids],
        #     'product_dimension_qty': line.product_dimension_qty
        # })
        return values