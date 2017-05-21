# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2016-2016 BADEP. All Rights Reserved.
#    Author: Khalid HAZAM <k.hazam@badep.ma>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api
from openerp.tools.safe_eval import safe_eval as eval

class AccountEdiTableau(models.Model):
    _name= 'account.edi.tableau'
    _description='Modele des tableaux dans la liasse fiscale marocaine'

    name = fields.Char(string='Nom')
    modele = fields.Selection([('normal','Comptable normal'),
                                           ('simplifie','Comptable simplifié'),
                                           ('financier','Etablissements Financiers'),
                                           ('assurance','Assurances')],string='Modèle')
    champs = fields.One2many(comodel_name='account.edi.champ', inverse_name='tableau')
    
    
class AccountEdiChamp(models.Model):
    _name = 'account.edi.champ'
    _description = 'Champ dans un tableau EDI'
    
    code=fields.Integer()
    tableau = fields.Many2one('account.edi.tableau')
    name=fields.Char(string='Nom')
    type = fields.Selection([('0','Calculabe'),
                                           ('1','Saisissable'),
                                           ('2','ExtraField Saisissable')],string='Modèle')
    formule=fields.Text()
    result=fields.Char(string="Dernier resultat")
    
    @api.one
    def calculate(self):
        localdict = {'object': self}
        eval(self.formule,localdict,mode='exec',nocopy=True)
        self.result = localdict['result']
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
