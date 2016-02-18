# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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
from openerp import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'
    rc = fields.Char(string='RC')
    pat = fields.Char(string='Patente')
    idf = fields.Char(string='IF')
    
class res_company(models.Model):
    _inherit = 'res.company'
    
    pat = fields.Char(string='Patente')
    ice = fields.Char(string='Identifiant Commun')
    cnss = fields.Char(string='CNSS')
    tampon = fields.Binary()
    
class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    with_stamp = fields.Boolean(string='Avec tampon')

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    with_stamp = fields.Boolean(string='Avec tampon')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
