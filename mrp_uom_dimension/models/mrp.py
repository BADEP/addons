from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = ['mrp.production', 'uom.line']
    _name = 'mrp.production'

    dimension_ids = fields.One2many('mrp.production.dimension', 'line_id', string='Dimensions', copy=True)

    def get_uom_field(self):
        return 'product_uom_id'
    def get_qty_field(self):
        return 'product_qty'

    @api.onchange('product_uom_id')
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

class MrpProductionDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'mrp.production.dimension'

    line_id = fields.Many2one('mrp.production', required=False, ondelete='cascade')

class ChangeProductionQty(models.TransientModel):
    _inherit = ['change.production.qty', 'uom.line']
    _name = 'change.production.qty'

    dimension_ids = fields.Many2many('mrp.production.dimension', 'change_production_qty_id')
    product_dimension_qty = fields.Integer('Nombre', required=True)
    product_uom_id = fields.Many2one('uom.uom', related='mo_id.product_uom_id')

    @api.onchange('product_uom_id')
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    def get_uom_field(self):
        return 'product_uom_id'
    def get_qty_field(self):
        return 'product_qty'

    @api.model
    def default_get(self, fields):
        res = super(ChangeProductionQty, self).default_get(fields)
        if res.get('mo_id'):
            res['product_dimension_qty'] = self.env['mrp.production'].browse(res['mo_id']).product_dimension_qty
            res['dimension_ids'] = [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in
                                    self.env['mrp.production'].browse(res['mo_id']).dimension_ids]
        return res

    def change_prod_qty(self):
        res = super().change_prod_qty()
        for wizard in self:
            wizard.mo_id.dimension_ids.unlink()
            wizard.mo_id.write({
                'product_dimension_qty': wizard.product_dimension_qty,
                'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in wizard.dimension_ids]
            })
        return res
