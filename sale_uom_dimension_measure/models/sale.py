from odoo import models, fields, api, exceptions, _
from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    measure_ids = fields.One2many('sale.measure', 'sale_order_id', string='Mesure')
    measure_count = fields.Integer(string='Nombre des mesures', compute='_compute_measure_ids')
    is_measured = fields.Boolean(string="Mesures faites", compute='_get_is_measured')

    @api.depends('order_line.is_measured')
    def _get_is_measured(self):
        for rec in self:
            rec.is_measured = any(line.is_measured for line in rec.order_line)

    def action_show_measures(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Mesures"),
            "res_model": "sale.measure",
            "domain": [('id', 'in', self.measure_ids.ids)],
            "view_mode": "tree,form", #,google_map
            "context": self.env.context,
        }

    @api.depends('measure_ids')
    def _compute_measure_ids(self):
        for measure in self:
            self.measure_count = len(measure.measure_ids)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    measure_start = fields.Datetime(string="Début mesures")
    measure_end = fields.Datetime(string="Fin mesures")
    measure_ids = fields.Many2many('sale.measure', string='Ordre de Prise de Mesure', copy=False,
                                   compute='get_measure_ids')
    measure_line_ids = fields.One2many('sale.measure.line', 'sale_order_line_id', copy=False, string='Lignes de prise de measure')
    is_measured = fields.Boolean(string="Mesures faites", compute='_get_is_measured')
    measure_line_count = fields.Integer(string="Mesures", compute='_get_measure_line_count')
    measured_line_count = fields.Integer(string="Qté mesurée", compute='_get_measure_line_count')
    measured_quantity = fields.Float(string="Qté mesurée", compute='_get_measured_quantity', digits='Product Unit of Measure')
    price_to_update = fields.Boolean(default=False, copy=False)
    to_launch = fields.Boolean(string="To Launch Procurement", compute='_get_to_launch')

    def get_dummy_qty(self):
        for rec in self:
            if rec.dimension_ids:
                return rec.product_dimension_qty * (rec.measured_quantity - rec.procurement_qty) / rec.product_uom_qty
            else:
                return super().get_dummy_qty()

    @api.depends('procurement_qty', 'measured_quantity')
    def _get_to_launch(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self.filtered(lambda l: l.dimension_ids):
            if line.order_id.state != 'sale' or float_compare(line.procurement_qty, line.measured_quantity, precision_digits=precision) >= 0:
                line.to_launch = False
            else:
                line.to_launch = True
        super(SaleOrderLine, self.filtered(lambda l: not l.dimension_ids))._get_to_launch()

    @api.onchange('price_unit')
    def onchange_set_to_update(self):
        self.price_to_update = False

    @api.depends('measure_line_ids')
    def get_measure_ids(self):
        for rec in self:
            rec.measure_ids = rec.order_id.mapped('measure_ids')

    @api.constrains('measure_start', 'measure_end')
    def _check_measure_dates(self):
        for rec in self:
            if rec.measure_end and rec.measure_start and rec.measure_end <= rec.measure_start:
                raise exceptions.ValidationError("La date Fin mesures doit étre supérieur à la date Début mesures")

    @api.depends('measured_quantity', 'product_uom_qty', 'product_id')
    def _get_is_measured(self):
        for rec in self:
            rec.is_measured = (rec.measure_line_count == rec.product_dimension_qty) or rec.product_id.to_measure == False

    @api.depends('measure_line_ids.state')
    def _get_measure_line_count(self):
        for rec in self:
            rec.measure_line_count = len(rec.measure_line_ids)
            rec.measured_line_count = len(rec.measure_line_ids.filtered(lambda ml: ml.state == 'done'))

    @api.depends('measure_line_ids', 'dimension_ids.quantity')
    def _get_measured_quantity(self):
        for rec in self:
            rec.measured_quantity = rec.product_uom.eval_values(dict([(d.dimension_id.id, d.quantity) for d in rec.dimension_ids]),
                                               rec.measured_line_count)

    def action_create_measures(self, quantity=0):
        if not isinstance(quantity,int):
            quantity = 0
        for rec in self:
            if not self.measure_ids.filtered(lambda m: m.state == 'draft'):
                measure_id = self.env['sale.measure'].create({
                    'sale_order_id': rec.order_id.id,
                    'measure_start': rec.measure_start,
                    'measure_end': rec.measure_end,
                })
            else:
                measure_id = self.measure_ids.filtered(lambda m: m.state == 'draft')[-1]
                measure_id.measure_ids.filtered(lambda x: x.state == 'draft' and x.sale_order_line_id.id == rec.id).unlink()
            number = min(quantity, rec.product_dimension_qty - rec.measured_line_count) if quantity else rec.product_dimension_qty - rec.measured_line_count
            measure_id.measure_ids = [(0, 0, {
                'sale_order_line_id': rec.id,
                'dimension_ids': [(0, 0, {
                    'dimension_id': d.dimension_id.id,
                    'quantity': 0,
                    'expected_quantity': d.quantity,
                }) for d in rec.dimension_ids]
            }) for d in range(number)]

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update({
            'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in
                              self.dimension_ids],
            'product_dimension_qty': self.measured_line_count,
        })
        return values


class StockMove(models.Model):
    _inherit = 'stock.move'

    # TODO: better method
    def _merge_moves_fields(self):
        res = super(StockMove, self)._merge_moves_fields()
        res.update({
            'product_dimension_qty': self.mapped('product_dimension_qty')[-1],
        })
        return res
