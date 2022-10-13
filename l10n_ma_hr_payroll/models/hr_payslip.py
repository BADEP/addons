from odoo import models, fields, api, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super().get_worked_day_lines(contracts, date_from, date_to)
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            attendances125 = {
                'name': _("Heures supp. à 125%"),
                'sequence': 1,
                'code': 'WORK125',
                'number_of_days': 0,
                'number_of_hours': 0,
                'contract_id': contract.id,
            }
            attendances150 = {
                'name': _("Heures supp. à 150%"),
                'sequence': 2,
                'code': 'WORK150',
                'number_of_days': 0,
                'number_of_hours': 0,
                'contract_id': contract.id,
            }
            attendances200 = {
                'name': _("Heures supp. à 200%"),
                'sequence': 3,
                'code': 'WORK200',
                'number_of_days': 0,
                'number_of_hours': 0,
                'contract_id': contract.id,
            }
            res.append(attendances125)
            res.append(attendances150)
            res.append(attendances200)
        return res


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    appears_on_payslip = fields.Boolean(string='Apparaît dans le bulletin de paie', related='salary_rule_id.appears_on_payslip', store=True)