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

    line_id = fields.Many2one('mrp.production', required=True, ondelete='cascade')