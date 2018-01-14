# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 BADEP (<http://www.badep.ma>).
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
from openerp.tools import amount_to_text_en

to_19_fr = (u'zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six',
          'sept', 'huit', 'neuf', 'dix', 'onze', 'douze', 'treize',
          'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf')
tens_fr = ('vingt', 'trente', 'quarante', 'Cinquante', 'Soixante', 'Soixante-dix', 'Quatre-vingts', 'Quatre-vingt Dix')
denom_fr = ('',
          'Mille', 'Millions', 'Milliards', 'Billions', 'Quadrillions',
          'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion',
          'Décillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quattuordecillion',
          'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion')

def _convert_nn_fr(val):
    """ convert a value < 100 to French
    """
    if val < 20:
        return to_19_fr[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
        if dval + 10 > val:
            if val % 10:
                if dval == 70 or dval == 90:
                    return tens_fr[dval / 10 - 3] + '-' + to_19_fr[val % 10 + 10]
                else:
                    return dcap + '-' + to_19_fr[val % 10]
            return dcap

def _convert_nnn_fr(val):
    """ convert a value < 1000 to french
    
        special cased because it is the level that kicks 
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        if rem == 1:
            word = 'Cent'
        else:
            word = to_19_fr[rem] + ' Cent'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_fr(mod)
    return word

def french_number(val):
    if val < 100:
        return _convert_nn_fr(val)
    if val < 1000:
        return _convert_nnn_fr(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_fr))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l == 1 and didx <=1:
                ret = denom_fr[didx]
            else:
                ret = _convert_nnn_fr(l) + ' ' + denom_fr[didx]
            if r > 0:
                ret = ret + ', ' + french_number(r)
            return ret

def amount_to_text_fr(number, currency):
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = french_number(abs(int(list[0])))
    end_word = french_number(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and ' Centimes' or ' Centime'
    final_result = start_word + ' ' + units_name + ' ' + end_word + ' ' + cents_name
    return final_result

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    amount_to_text = fields.Char(compute='_amount_in_words', string='In Words', help="The amount in words")
    
    @api.depends('amount_total','partner_id','partner_id.lang')
    @api.one
    def _amount_in_words(self):
        if self.partner_id.lang == 'fr_FR':
            self.amount_to_text = amount_to_text_fr(self.amount_total, self.currency_id.label)
        elif self.partner_id.lang == 'en_US':
            self.amount_to_text = amount_to_text_en.amount_to_text(nbr=self.amount_total, currency=self.currency_id.label)
AccountInvoice()

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    amount_to_text = fields.Char(compute='_amount_in_words', string='In Words', help="The amount in words")
    
    @api.depends('amount_total')
    @api.one
    def _amount_in_words(self):
        if self.partner_id.lang == 'fr_FR':
            self.amount_to_text = amount_to_text_fr(self.amount_total, self.pricelist_id.currency_id.label)
        elif self.partner_id.lang == 'en_US':
            self.amount_to_text = amount_to_text_en.amount_to_text(nbr=self.amount_total, currency=self.pricelist_id.currency_id.label)
SaleOrder()

class ResLang(models.Model):
    _inherit = 'res.lang'
    
    amount_prefix = fields.Char()
    amount_suffix = fields.Char()
ResLang()

class ResCurrency(models.Model):
    _inherit = 'res.currency'
    
    @api.one
    def get_default_label(self):
        self.label = self.name
    
    label = fields.Char(default = get_default_label)
ResCurrency()