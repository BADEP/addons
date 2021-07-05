from odoo import models, fields, api, exceptions, _
import time, datetime, dateutil, numpy
from odoo.tools import safe_eval

DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment
#  - record: Uom record
#  - product_dimension_qty: Number of products
#  - dimension_values: dict of dimension values with dimension key
#  - time, datetime, dateutil, numpy: useful Python libraries
#  - Warning: Warning Exception to use with raise
#  - result: return result
#  Example (Total perimeter of a window with regard of the quantity wanted): result = 2 * dimension_values[dimension_ids[0].id] * (dimension_values[dimension_ids[1].id] + dimension_values[dimension_ids[2].id])
#  Example (Total surface of a window with regard of the quantity wanted): result = numpy.prod(dimension_values.values()) \n\n\n\n"""


class UomUom(models.Model):
    _inherit = 'uom.uom'

    dimension_ids = fields.One2many('uom.dimension', 'parent_uom_id', string='Dimensions', copy=True)
    calculation_type = fields.Selection([('simple', 'Simple'), ('code', 'Code')], default='simple', required=True, string='Calculation Type')
    code = fields.Text(string='Python Code', default=DEFAULT_PYTHON_CODE)

    def eval_values(self, dimension_values, product_dimension_qty=1):
        for uom in self:
            if uom.calculation_type == 'simple':
                code = 'result = product_dimension_qty * numpy.prod(list(dimension_values.values()))'
            else:
                code = uom.code
            eval_context = {
                'env': self.env,
                'datetime': safe_eval.datetime,
                'dateutil': safe_eval.dateutil,
                'time': safe_eval.time,
                'numpy': safe_eval.wrap_module(__import__('numpy'), ['prod']),
                'Warning': exceptions.Warning,
                'record': uom,
                'product_dimension_qty': product_dimension_qty,
                'dimension_values': dimension_values,
                'result': 0,
            }
            # try:
            safe_eval.safe_eval(code, eval_context, mode="exec", nocopy=True)
            return float(eval_context['result'])
            # except, e:
            #     raise exceptions.UserError(_('Wrong python code defined for uom %s.') % (uom.name))


class UomDimension(models.Model):
    _name = 'uom.dimension'
    name = fields.Char(required=True)
    uom_id = fields.Many2one('uom.uom', required=True)
    parent_uom_id = fields.Many2one('uom.uom', required=True)
