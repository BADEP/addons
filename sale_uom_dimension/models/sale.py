from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line', 'uom.line']
    _name = 'sale.order.line'

    _uom_field = 'product_uom'
    _qty_field = 'product_uom_qty'

    dimension_ids = fields.One2many('sale.order.line.dimension', 'line_id', string='Dimensions', copy=True)

    @api.depends(_qty_field)
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.onchange(_uom_field)
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        values.update({
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in
                              self.dimension_ids],
            'product_dimension_qty': self.product_dimension_qty
        })
        return values

    def _prepare_invoice_line(self, **optional_values):
        optional_values.update({
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in
                              self.dimension_ids],
            #'product_dimension_qty': self.product_dimension_qty
        })
        return super()._prepare_invoice_line(**optional_values)

class SaleOrderLineDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'sale.order.line.dimension'

    line_id = fields.Many2one('sale.order.line', required=True, ondelete='cascade')