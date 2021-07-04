from odoo import models, fields

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    appears_on_payslip = fields.Boolean(string='Apparaît dans le bulletin de paie', related='salary_rule_id.appears_on_payslip', store=True)