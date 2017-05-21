from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_contract(models.Model):
    _inherit = 'hr.contract'
    _name = 'hr.contract'

    int1 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité Non taxable 1",default=0)
    int2 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité Non taxable 2",default=0)
    int3 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité Non taxable 3",default=0)
    int4 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité Non taxable 4",default=0)
    int5 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité Non taxable 5",default=0)
    it1 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité taxable 1",default=0)
    it2 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité taxable 2",default=0)
    it3 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité taxable 3",default=0)
    it4 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité taxable 4",default=0)
    it5 = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité taxable 5",default=0)

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    matricule_cimr = fields.Char(string="Numéro CIMR", required=False)
    matricule_mut = fields.Char(string="Numéro MUTUELLE", required=False)
    
class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _order = 'sequence asc'
    
class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'
    
    sequence = fields.Integer('Sequence',required=True,default=5)
    
    _order = 'sequence asc'