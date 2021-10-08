from odoo import models, fields, api

class AccountInvoiceLine(models.Model):
    _inherit = ['account.invoice.line', 'uom.line']
    _name = 'account.invoice.line'

    dimension_ids = fields.One2many('account.invoice.line.dimension', 'line_id', string='Dimensions', copy=True)

    def get_uom_field(self):
        return 'uom_id'
    def get_qty_field(self):
        return 'quantity'

    @api.onchange('uom_id')
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

class AccountInvoiceLineDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'account.invoice.line.dimension'

    line_id = fields.Many2one('account.invoice.line', required=True, ondelete='cascade')