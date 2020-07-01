from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    _name = 'res.company'
   
    plafond_secu = fields.Float(string="Plafond de la Securite Sociale", required=True, default=6000)
    nombre_employes = fields.Integer(string="Nombre d'employes")
    cotisation_prevoyance = fields.Float(string="Cotisation Patronale Prevoyance")
    org_ss = fields.Char(string="Organisme de sécurite sociale")
    conv_coll = fields.Char(string="Convention collective")
