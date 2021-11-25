from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = ['mrp.production', 'uom.line']
    _name = 'mrp.production'

    _uom_field = 'product_uom_id'
    _qty_field = 'product_qty'

    dimension_ids = fields.One2many('mrp.production.dimension', 'line_id', string='Dimensions', copy=True)

    @api.depends(_qty_field)
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.onchange(_uom_field)
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get('dimension_ids') or vals.get('product_dimension_qty'):
            for rec in res:
                dimension_commands = [(5,)]
                dimension_commands.extend([(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in rec.dimension_ids])
                rec.move_finished_ids.write({
                    'product_dimension_qty': rec.product_dimension_qty,
                    'dimension_ids': dimension_commands
                })
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get('dimension_ids') or vals.get('product_dimension_qty'):
            for rec in self:
                dimension_commands = [(5,)]
                dimension_commands.extend([(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in rec.dimension_ids])
                rec.move_finished_ids.write({
                    'product_dimension_qty': rec.product_dimension_qty,
                    'dimension_ids': dimension_commands
                })
        return res

    # todo: fix this and replace write
    # def _get_move_finished_values(self, product_id, product_uom_qty, product_uom, operation_id=False, byproduct_id=False):
    #     res = super()._get_move_finished_values(product_id, product_uom_qty, product_uom, operation_id, byproduct_id)
    #     dimension_commands = [(5,)]
    #     dimension_commands.extend([(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in self.dimension_ids])
    #     res.update({
    #         'product_dimension_qty': self.product_dimension_qty,
    #         'dimension_ids': dimension_commands
    #     })
    #     return res

class MrpProductionDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'mrp.production.dimension'

    line_id = fields.Many2one('mrp.production', required=True, ondelete='cascade')