from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    #not pretty but vals.pop('invoice_line_ids', None) does not leave us any alternative
    def write(self, vals):
        if vals.get('invoice_line_ids'):
            for line_val in vals['invoice_line_ids']:
                #modified line are not reported in line_ids so we copy them manually
                if line_val[0] != 0 and line_val[2] and line_val[2].get('dimension_ids'):
                    to_remove = []
                    for dim_val in line_val[2]['dimension_ids']:
                        if dim_val[0] == 0:
                            to_remove.append(dim_val)
                    for x in to_remove:
                        line_val[2]['dimension_ids'].remove(x)
                    vals['line_ids'].append(line_val)
        return super().write(vals)

class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "uom.line"]
    _name = 'account.move.line'

    _uom_field = 'product_uom_id'
    _qty_field = 'quantity'

    dimension_ids = fields.One2many('account.move.line.dimension', 'line_id', string='Dimensions', copy=True)

    @api.depends(_qty_field)
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.onchange(_uom_field)
    def onchange_product_uom_set_dimensions(self):
        super().onchange_product_uom_set_dimensions()

    def write(self, vals):
        return super().write(vals)

class AccountMoveLineDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'account.move.line.dimension'

    line_id = fields.Many2one('account.move.line', required=True, ondelete='cascade')