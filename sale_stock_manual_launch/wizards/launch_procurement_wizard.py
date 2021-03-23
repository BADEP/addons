from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class LaunchProcurementWizard(models.TransientModel):
    _name = 'launch.procurement.wizard'
    _description = 'Launch procurement wizard'

    line_ids = fields.One2many('launch.procurement.wizard.line', 'wizard_id', 'Lignes')

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("Vous ne pouvez créer des approvisionnements pour une commande à la fois."))
        res = super(LaunchProcurementWizard, self).default_get(fields)

        so = self.env['sale.order'].browse(self.env.context.get('active_id'))
        line_ids = []
        if so:
            line_fields = [f for f in self.env['launch.procurement.wizard.line']._fields.keys()]
            sale_order_line_id = self.env['sale.order.line'].default_get(line_fields)
            for line in so.order_line.filtered(lambda l: l.to_launch):
                line_data = dict(sale_order_line_id)
                line_data.update({
                        'sale_order_line_id': line.id,
                        'quantity': line.get_dummy_qty()[0],
                    })
                line_ids.append((0, 0, line_data))
            if 'line_ids' in fields:
                res.update({'line_ids': line_ids})
        return res

    def launch_procurement(self):
        for line in self.line_ids:
            line.sale_order_line_id.with_context(qty_to_launch=line.quantity).action_launch_procurement()

class LaunchProcurementWizardLine(models.TransientModel):
    _name = 'launch.procurement.wizard.line'
    _description = 'Launch procurement wizard line'

    wizard_id = fields.Many2one('launch.procurement.wizard', string="Wizard")
    sale_order_line_id = fields.Many2one('sale.order.line', string="Ligne de commande")
    quantity = fields.Integer(string="Quantité")

    @api.constrains('quantity')
    def _check_max_qty(self):
        for rec in self:
            if rec.quantity > rec.sale_order_line_id.product_uom_qty:
                raise ValidationError("Vous ne pouvez pas lancer en approvisionnement plus que la quantité restante: %s" % (rec.sale_order_line_id.product_uom_qty - rec.sale_order_line_id.procurement_qty))

