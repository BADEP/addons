# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    dimension_ids = fields.Many2many('uom.dimension',  domain="[('product_uom', '=', parent.product_uom)]")
        
class MrpProduction(models.Model):
    _inherit = "mrp.production"
    dimension_ids = fields.One2many('mrp.production.dimension','mrp_production')
    product_dimension_qty = fields.Integer('Nombre', required=True, default=0)

class MrpProductionDimension(models.Model):
    _name = "mrp.production.dimension"

    dimension_id = fields.Many2one('uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Integer('Quantité', required=True)
    mrp_production = fields.Many2one('mrp.production', required=True, ondelete='cascade')
    name = fields.Char(compute='get_name', store=True)
    display_name = fields.Char(compute='get_name', store=True)

    @api.depends('dimension_id', 'quantity')
    def get_name(self):
        for rec in self.filtered(lambda d: d.dimension_id):
            rec.display_name = rec.dimension_id.name + ': ' + str(rec.quantity)
            rec.name = rec.dimension_id.name + ': ' + str(rec.quantity)

class MrpBom(models.Model):
    _inherit = 'mrp.bom'