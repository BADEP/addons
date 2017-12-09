from openerp import models, fields


class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    is_driver = fields.Boolean(default=False)
hr_employee()
