from odoo import models, fields, api

class UomLine(models.AbstractModel):
    _name = 'uom.line'
    _description = 'UoM Line Mixin'

    _product_field = 'product_id'
    _uom_field = 'uom_id'
    _qty_field = 'product_uom_qty'

    dimension_ids = fields.One2many('uom.line.dimension', 'line_id', string='Dimensions', copy=True)
    product_dimension_qty = fields.Float('Nombre', required=True, default=0, compute='_get_product_dimension_qty', inverse='onchange_dimension_ids')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        for dim_values in res.get('dimension_ids', []):
            if dim_values[0] == 6:
                res['dimension_ids'].remove(dim_values)
        return res

    @api.onchange('product_dimension_qty', 'dimension_ids')
    def onchange_dimension_ids(self):
         for rec in self.filtered(lambda ul: ul.dimension_ids and ul.product_dimension_qty):
            rec[rec._qty_field] = rec._compute_qty()

    def _get_product_dimension_qty(self):
        for rec in self:
            qty = rec._compute_qty(1)
            rec.product_dimension_qty = round(rec[self._qty_field] / qty, 0) if qty else rec.product_dimension_qty

    def _compute_qty(self, force_qty=None):
        self.ensure_one()
        force_qty = force_qty or self.product_dimension_qty
        if self.dimension_ids:
            if self._product_field in self:
                custom_code = self[self._product_field].custom_uom_code and self[self._product_field].custom_uom_code or None
            else:
                custom_code = None
            return self[self._uom_field].eval_values(dict([(d.dimension_id.id, d.quantity) for d in self.dimension_ids]), force_qty, custom_code)
        return 1

    @api.onchange(_uom_field)
    def onchange_product_uom_set_dimensions(self):
        product_uom = self[self._uom_field]
        if self.dimension_ids and product_uom and sorted(self.dimension_ids.mapped('dimension_id.id')) == sorted(product_uom.dimension_ids.ids):
            return
        self.dimension_ids = [(5, 0, 0)]
        if product_uom:
            self.dimension_ids = [(0, 0, {'dimension_id': d.id}) for d in product_uom.dimension_ids]

class UomLineDimension(models.AbstractModel):
    _name = 'uom.line.dimension'
    _description = 'UoM Dimension Line Mixin'

    line_id = fields.Many2one('uom.line', copy=True)
    dimension_id = fields.Many2one('uom.dimension', required=True, ondelete='cascade')
    quantity = fields.Float('Quantité', required=True, digits='Product Unit of Measure')
    name = fields.Char(compute='get_name', store=True)
    display_name = fields.Char(compute='get_name', store=True)

    @api.depends('dimension_id', 'quantity')
    def get_name(self):
        for rec in self.filtered(lambda d: d.dimension_id):
            rec.display_name = rec.dimension_id.name + ': ' + str(round(rec.quantity, 3))
            rec.name = rec.dimension_id.name + ': ' + str(round(rec.quantity, 3))
