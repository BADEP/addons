# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing det


from odoo import fields, models,api
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _
from odoo.exceptions import UserError
	
class hr_contract(models.Model):
    _inherit = 'hr.contract'

	
    
		
		
class res_company(models.Model):
    _inherit = 'res.company'
    _name = 'res.company'
   
    plafond_secu = fields.Float(string="Plafond de la Securite Sociale", required=True, default=6000)
    nombre_employes = fields.Integer(string="Nombre d'employes")
    cotisation_prevoyance = fields.Float(string="Cotisation Patronale Prevoyance")
    org_ss = fields.Char(string="Organisme de sécurite sociale")
    conv_coll = fields.Char(string="Convention collective")

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    
    payment_mode = fields.Char('Mode de paiement', required=False)
  

class hr_employee(models.Model):
    _inherit = 'hr.employee'

	
   
    cin = fields.Char(string="Numéro CIN", required=False)
    matricule_cnss = fields.Char(string="Numéro CNSS", required=False)
    matricule_cimr = fields.Char(string="Numéro CIMR", required=False)
    matricule_mut = fields.Char(string="Numéro MUTUELLE", required=False)
    num_chezemployeur = fields.Integer(string="Matricule")
    abs = fields.Integer(string="Absence en heures" ,default=0)
    hs25 = fields.Integer(string="Heures sup à 25" ,default=0)
    hs50 = fields.Integer(string="Heures sup à 50",default=0)
    hs100 = fields.Integer(string="Heures sup à 100",default=0)
    av_sal = fields.Integer(string="Avance sur Salaire",default=0)   
    rem_mut = fields.Integer(string="Remboursement Mutuelle",default=0)
   	
	
    
		

		
		
		
	
