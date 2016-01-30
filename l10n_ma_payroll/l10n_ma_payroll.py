
from datetime import timedelta
from openerp import models, fields, api

class hr_contract(models.Model):
    _inherit = 'hr.contract'
    _name = 'hr.contract'
	
    # start_date = fields.Date(string="Date d'embauche (=Durée)", related='date_start',readonly=True)
    # prime_saliss = fields.Integer(string="Prime Salissure",default=0)
    # prime_vest = fields.Integer(string="Prime Vestimentaire",default=0)
    # prime_repr = fields.Float(string="Prime de représentation",default=0)
    # taux_cimr = fields.Float(string="Taux CIMR",default=3)
    # taux_mut = fields.Float(string="Taux Mutuelle",default=3)
    # prime_transport = fields.Integer(string="Prime de Transport")
    # prime_encad = fields.Integer(string="Prime d'encadrement")
    # anciennete = fields.Float(string="Ancienneté", compute='_anciennete')
    # end_date = fields.Date(default=fields.Date.today)
		
		
    # @api.one
    # @api.depends('start_date','end_date','date_start')
    # def _anciennete(self):
        # if not (self.start_date and self.end_date): 
            # self.end_date = self.start_date
            # return
        # start_date = fields.Datetime.from_string(self.date_start)
	# end_date = fields.Datetime.from_string(self.end_date)
        # self.anciennete = (end_date - start_date).days/365.2425
		
		
class res_company(models.Model):
    _inherit = 'res.company'
    _name = 'res.company'
   
    plafond_secu = fields.Float(string="Plafond de la Securite Sociale", required=True)
    nombre_employes = fields.Integer(string="Nombre d'employes")
    cotisation_prevoyance = fields.Float(string="Cotisation Patronale Prevoyance")
    org_ss = fields.Char(string="Organisme de sécurite sociale")
    # t_pat = fields.Float(string="Taux CNSS Patronal")
    # t_sal = fields.Float(string="Taux CNSS Salarial")
    conv_coll = fields.Char(string="Convention collective")

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
    _name = 'hr.payslip'
    
    payment_mode = fields.Char('Mode de paiement', required=False)
  

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    _name = 'hr.employee'
	
    first_name = fields.Char(string="Prénom", required=True)
    last_name = fields.Char(string="Nom", required=True)
    cin = fields.Char(string="Numéro CIN", required=True)
    matricule_cnss = fields.Integer(string="Numéro CNSS", required=True)
    matricule_cimr = fields.Integer(string="Numéro CIMR", required=True)
    matricule_mut = fields.Integer(string="Numéro MUTUELLE", required=True)
    num_chezemployeur = fields.Integer(string="Matricule")
    abs = fields.Integer(string="Absence en heures" ,default=0)
    hs25 = fields.Integer(string="Heures sup à 25" ,default=0)
    hs50 = fields.Integer(string="Heures sup à 50",default=0)
    hs100 = fields.Integer(string="Heures sup à 100",default=0)
    av_sal = fields.Integer(string="Avance sur Salaire",default=0)   
    rem_mut = fields.Integer(string="Remboursement Mutuelle",default=0)
    complete_name = fields.Char(string="Nom Complet", compute='_complete_name')	
	
    @api.one
    @api.depends('first_name','last_name','name')
    def _complete_name(self):
	    if self.last_name :
		self.complete_name = self.first_name + " " + self.last_name
 
    @api.onchange('complete_name', 'name') # if these fields are changed, call method
    def check_change(self):     
        if self.name < self.complete_name:
		self.name = self.complete_name	
		

		
		
		
	
