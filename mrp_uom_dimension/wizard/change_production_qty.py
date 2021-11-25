from odoo import models, fields, api

class ChangeProductionQty(models.TransientModel):
    _inherit = ['change.production.qty', 'uom.line']
    _name = 'change.production.qty'

    _uom_field = 'product_uom_id'
    _qty_field = 'product_qty'

    dimension_ids = fields.One2many('change.production.qty.dimension', 'line_id')
    product_uom_id = fields.Many2one('uom.uom', related='mo_id.product_uom_id')
    product_id = fields.Many2one('product.product', related='mo_id.product_id')

    @api.depends(_qty_field)
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.onchange(_uom_field)
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    @api.model
    def default_get(self, fields):
        res = super(ChangeProductionQty, self).default_get(fields)
        if res.get('mo_id'):
            res['product_dimension_qty'] = self.env['mrp.production'].browse(res['mo_id']).product_dimension_qty
            res['dimension_ids'] = [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in
                                    self.env['mrp.production'].browse(res['mo_id']).dimension_ids]
        return res

    @api.model
    def create(self, vals):
        return super().create(vals)

    def change_prod_qty(self):
        res = super().change_prod_qty()
        for wizard in self:
            wizard.mo_id.dimension_ids.unlink()
            wizard.mo_id.write({
                'product_dimension_qty': wizard.product_dimension_qty,
                'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in wizard.dimension_ids]
            })
        return res

class ChangeProductionQtyDimension(models.TransientModel):
    _inherit = 'uom.line.dimension'
    _name = 'change.production.qty.dimension'

    line_id = fields.Many2one('change.production.qty', required=True, ondelete='cascade')