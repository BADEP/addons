from odoo import models, fields, api

class MrpBomLine(models.Model):
    _inherit = ['mrp.bom.line', 'uom.line']
    _name = 'mrp.bom.line'

    _uom_field = 'product_uom_id'
    _qty_field = 'product_qty'

    dimension_ids = fields.One2many('mrp.bom.line.dimension', 'line_id', string='Dimensions', copy=True)

    @api.depends('product_qty')
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.onchange('product_uom_id')
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

class MrpProductionDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'mrp.bom.line.dimension'

    line_id = fields.Many2one('mrp.bom.line', required=True, ondelete='cascade')