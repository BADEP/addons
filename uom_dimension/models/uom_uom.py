# -*- coding: utf-8 -*-

from odoo import models, fields, api
import numpy

DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment
#  - dimension_values: dict of dimension values with dimension key
#  - dimension_ids: record set of the UoM dimensions
#  - time, datetime, dateutil, timezone, numpy: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
#  - result: return result
#  Example (Total perimeter of a window with regard of the quantity wanted): result = 2 * dimension_values[dimension_ids[0].id] * (dimension_values[dimension_ids[1].id] + dimension_values[dimension_ids[2].id])
#  Example (Total surface of a window with regard of the quantity wanted): result = numpy.prod(dimension_values.values()) \n\n\n\n"""

class ProductUom(models.Model):
    _inherit = "uom.uom"
    
    dimension_ids = fields.One2many('uom.dimension', 'uom_id', copy=True)
    type = fields.Selection([('simple', 'Simple', 'code', 'Code')])
    code = fields.Text(string='Python Code', default=DEFAULT_PYTHON_CODE)

class ProductUomDimension(models.Model):
    _name = 'uom.dimension'
    name = fields.Char(required=True)
    uom_id = fields.Many2one('uom.uom', required=True)