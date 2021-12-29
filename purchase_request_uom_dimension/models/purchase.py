from odoo import models, fields, api

class PurchaseRequestLine(models.Model):
    _inherit = ['purchase.request.line', 'uom.line']
    _name = 'purchase.request.line'

    _uom_field = 'product_uom_id'
    _qty_field = 'product_qty'

    dimension_ids = fields.One2many('purchase.request.line.dimension', 'line_id', string='Dimensions', copy=True)

    @api.depends(_qty_field)
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.onchange(_uom_field)
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()


class PurchaseRequestLineDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'purchase.request.line.dimension'

    line_id = fields.Many2one('purchase.request.line', required=True, ondelete='cascade')