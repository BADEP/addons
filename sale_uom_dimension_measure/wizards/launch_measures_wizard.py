from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class LaunchMeasureWizard(models.TransientModel):
    _name = 'launch.measures.wizard'
    _description = 'Launch measures wizard'

    measure_line_ids = fields.One2many('launch.measures.wizard.line', 'wizard_id', 'Lignes')

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("Vous ne pouvez créer des ordres de prise de mesure que pour une commande à la fois."))
        res = super(LaunchMeasureWizard, self).default_get(fields)

        so = self.env['sale.order'].browse(self.env.context.get('active_id'))
        measure_line_ids = []
        if so:
            line_fields = [f for f in self.env['launch.measures.wizard.line']._fields.keys()]
            sale_order_line_id = self.env['sale.order.line'].default_get(line_fields)
            for line in so.order_line.filtered(lambda l: not l.is_measured):
                measure_line_data = dict(sale_order_line_id)
                measure_line_data.update({
                        'sale_order_line_id': line.id,
                        'quantity': line.product_dimension_qty - line.measured_line_count,
                    })
                measure_line_ids.append((0, 0, measure_line_data))
            if 'measure_line_ids' in fields:
                res.update({'measure_line_ids': measure_line_ids})
        return res

    def create_measure(self):
        for line in self.measure_line_ids:
            line.sale_order_line_id.action_create_measures(line.quantity)

class launch_measures_wizard_line(models.TransientModel):
    _name = 'launch.measures.wizard.line'
    _description = 'Launch measures wizard line'

    wizard_id = fields.Many2one('launch.measures.wizard', string="Mesure")
    sale_order_line_id = fields.Many2one('sale.order.line', string="Ligne de commande")
    quantity = fields.Integer(string="Quantité")

    @api.constrains('quantity')
    def _check_max_qty(self):
        for rec in self:
            if rec.quantity > rec.sale_order_line_id.product_dimension_qty - rec.sale_order_line_id.measured_line_count:
                raise ValidationError("Vous ne pouvez pas créer plus que la quantité globale restante à mesurer: %s" % (rec.sale_order_line_id.product_dimension_qty - rec.sale_order_line_id.measured_line_count))