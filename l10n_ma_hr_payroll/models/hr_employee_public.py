from odoo import models, fields

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    cin = fields.Char(string="Numéro CIN", required=False)