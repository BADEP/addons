from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_contract(models.Model):
    _inherit = 'hr.contract'
    _name = 'hr.contract'

    indemnite_saliss = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité Salissure",default=0)
    indemnite_vest = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité Vestimentaire",default=0)
    indemnite_repr = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité de représentation",default=0)
    indemnite = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnités divers",default=0)
    indemnite_transport = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité de Transport",default=0)
    indemnite_encad = fields.Float(digits_compute=dp.get_precision('Account'), string="Indemnité d'encadrement",default=0)

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    matricule_cimr = fields.Char(string="Numéro CIMR", required=False)
    matricule_mut = fields.Char(string="Numéro MUTUELLE", required=False)