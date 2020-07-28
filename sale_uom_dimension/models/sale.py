from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    dimension_ids = fields.One2many('sale.order.line.dimension', 'sale_order_line_id', string='Dimensions', copy=True)

    @api.onchange('dimension_ids')
    def onchange_dimension_ids(self):
        if self.dimension_ids:
            qty = self.product_uom.eval_values(dict([(d.dimension_id.id, d.quantity) for d in self.dimension_ids]))
            qty_delivered_manual = self.product_uom.eval_values(dict([(d.dimension_id.id, d.quantity_delivered) for d in self.dimension_ids]))
            if qty != self.product_uom_qty:
                self.product_uom_qty = qty
            if qty_delivered_manual != self.product_uom_qty:
                self.qty_delivered_manual = qty_delivered_manual

    @api.onchange('product_uom')
    def onchange_product_uom_set_dimensions(self):
        self.dimension_ids = [(5, 0, 0)]
        if self.product_uom:
            self.dimension_ids = [(0, 0, {'dimension_id':d.id}) for d in self.product_uom.dimension_ids]

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update({
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity})  for d in self.dimension_ids],
        })
        return values

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity})  for d in self.dimension_ids],
        })
        return res

class SaleOrderLineDimension(models.Model):
    _name = 'sale.order.line.dimension'
    dimension_id = fields.Many2one('uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', required=True, digits=dp.get_precision('Product Unit of Measure'))
    quantity_delivered = fields.Float('Quantité livrée', digits=dp.get_precision('Product Unit of Measure'))
    sale_order_line_id = fields.Many2one('sale.order.line', required=True, ondelete='cascade')
    name = fields.Char(compute='get_name', store=True)
    display_name = fields.Char(compute='get_name', store=True)
    qty_delivered_method = fields.Selection(related='sale_order_line_id.qty_delivered_method')

    @api.depends('dimension_id', 'quantity')
    def get_name(self):
        for rec in self.filtered(lambda d: d.dimension_id):
            rec.display_name = rec.dimension_id.name + ': ' + str(rec.quantity)
            rec.name = rec.dimension_id.name + ': ' + str(rec.quantity)