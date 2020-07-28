from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    dimension_ids = fields.One2many('account.invoice.line.dimension', 'invoice_line_id', string='Dimensions', copy=True)

    @api.onchange('dimension_ids')
    def onchange_dimension_ids(self):
        if self.dimension_ids:
            qty = self.uom_id.eval_values(dict([(d.dimension_id.id, d.quantity) for d in self.dimension_ids]))
            if qty != self.quantity:
                self.quantity = qty

    @api.onchange('uom_id')
    def onchange_uom(self):
        self.dimension_ids = [(5, 0, 0)]
        if self.uom_id:
            self.dimension_ids = [(0, 0, {'dimension_id':d.id, 'invoice_line_id': self.id}) for d in self.uom_id.dimension_ids]

class AccountInvoiceLineDimension(models.Model):
    _name = 'account.invoice.line.dimension'

    dimension_id = fields.Many2one('uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', required=True, digits=dp.get_precision('Product Unit of Measure'))
    invoice_line_id = fields.Many2one('account.invoice.line', required=True, ondelete='cascade')
    name = fields.Char(compute='get_name', store=True)
    display_name = fields.Char(compute='get_name', store=True)

    @api.depends('dimension_id', 'quantity')
    def get_name(self):
        for rec in self.filtered(lambda d: d.dimension_id):
            rec.display_name = rec.dimension_id.name + ': ' + str(rec.quantity)
            rec.name = rec.dimension_id.name + ': ' + str(rec.quantity)