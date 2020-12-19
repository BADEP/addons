# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class StockMove(models.Model):
    _inherit = 'stock.move'
    dimension_ids = fields.One2many('stock.move.dimension', 'stock_move_id', copy=True)
    product_dimension_qty = fields.Integer('Nombre initial')
    product_dimension_qty_done = fields.Integer('Nombre fait', required=True, default=0, copy=False)

    @api.depends('state', 'picking_id', 'product_id')
    def _compute_is_quantity_done_editable(self):
        for rec in self:
            rec.is_quantity_done_editable = True

    @api.depends('product_id', 'has_tracking')
    def _compute_show_details_visible(self):
        res = super()._compute_show_details_visible()
        for move in self.filtered(lambda m: m.dimension_ids):
            move.show_details_visible = False
        return res

    @api.onchange('dimension_ids', 'product_dimension_qty_done')
    def onchange_dimensions(self):
        if self.dimension_ids and self.product_dimension_qty:
            self.quantity_done = (self.product_dimension_qty_done * self.product_uom_qty) / self.product_dimension_qty

    def _prepare_procurement_values(self):
        res = super(StockMove, self)._prepare_procurement_values()
        res.update({
            'product_dimension_qty': self.product_dimension_qty,
            'dimension_ids': [(0, 0, {'dimension_id':d.dimension_id.id, 'quantity':d.quantity}) for d in self.dimension_ids]
        })
        return res

class StockMoveDimension(models.Model):
    _name = "stock.move.dimension"

    dimension_id = fields.Many2one('uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', required=True)
    stock_move_id = fields.Many2one('stock.move', required=True, ondelete='cascade')
    name = fields.Char(compute='get_name', store=True)
    display_name = fields.Char(compute='get_name', store=True)

    @api.depends('dimension_id', 'quantity')
    def get_name(self):
        for rec in self.filtered(lambda d: d.dimension_id):
            rec.display_name = rec.dimension_id.name + ': ' + str(rec.quantity)
            rec.name = rec.dimension_id.name + ': ' + str(rec.quantity)

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['dimension_ids', 'product_dimension_qty']
        return fields