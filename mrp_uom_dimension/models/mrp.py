from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = "mrp.production"
    dimension_ids = fields.One2many('mrp.production.dimension', 'mrp_production')
    product_dimension_qty = fields.Integer('Nombre', required=True, default=0)

    @api.onchange('product_dimension_qty', 'dimension_ids')
    def onchange_dimension_ids(self):
        if self.dimension_ids:
            qty = self.product_uom_id.eval_values(
                dict([(d.dimension_id.id, d.quantity) for d in self.dimension_ids]), self.product_dimension_qty)
            if qty != self.product_qty:
                self.product_qty = qty

    @api.onchange('product_uom_id')
    def onchange_product_uom(self):
        self.dimension_ids = [(5, 0, 0)]
        if self.product_uom_id:
            self.dimension_ids = [(0, 0, {'dimension_id': d.id}) for d in self.product_uom_id.dimension_ids]

class MrpProductionDimension(models.Model):
    _name = "mrp.production.dimension"

    dimension_id = fields.Many2one('uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', required=True)
    mrp_production = fields.Many2one('mrp.production', ondelete='cascade')
    name = fields.Char(compute='get_name', store=True)
    display_name = fields.Char(compute='get_name', store=True)

    @api.depends('dimension_id', 'quantity')
    def get_name(self):
        for rec in self.filtered(lambda d: d.dimension_id):
            rec.display_name = rec.dimension_id.name + ': ' + str(rec.quantity)
            rec.name = rec.dimension_id.name + ': ' + str(rec.quantity)


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    dimension_ids = fields.Many2many('mrp.production.dimension', 'change_production_qty_id')
    product_dimension_qty = fields.Integer('Nombre', required=True)

    @api.model
    def default_get(self, fields):
        res = super(ChangeProductionQty, self).default_get(fields)
        if res.get('mo_id'):
            res['product_dimension_qty'] = self.env['mrp.production'].browse(res['mo_id']).product_qty
            res['dimension_ids'] = [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in
                                    self.env['mrp.production'].browse(res['mo_id']).dimension_ids]
        return res

    @api.onchange('product_dimension_qty', 'dimension_ids')
    def onchange_dimension_ids(self):
        if self.dimension_ids:
            qty = self.mo_id.product_uom_id.eval_values(
                dict([(d.dimension_id.id, d.quantity) for d in self.dimension_ids]), self.product_dimension_qty)
            if qty != self.product_qty:
                self.product_qty = qty

    def change_prod_qty(self):
        res = super().change_prod_qty()
        for wizard in self:
            wizard.mo_id.dimension_ids.unlink()
            wizard.mo_id.write({
                'product_dimension_qty': wizard.product_dimension_qty,
                'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in wizard.dimension_ids]
            })
        return res
