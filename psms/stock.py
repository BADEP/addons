# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class stock_location_pump(models.Model):
    _name = 'stock.location.pump'
    
    location = fields.Many2one('stock.location', required=True, ondelete='cascade', string="Emplacement", domain=[('usage', '=', 'internal'), ('active', '=', True)])
    counter = fields.Float(digits_compute=dp.get_precision('Product UoS'), required=True, default=0, string="Compteur")
    name = fields.Char(string="Nom")
    product = fields.Many2one('product.product', ondelete='set null', string="Article")
    logs = fields.One2many('sale.session.log', 'pump')
    electric_diff = fields.Float(digits_compute=dp.get_precision('Product UoS'), required=True, default=0, string="Décalage électrique")
    electric_counter = fields.Float(digits_compute=dp.get_precision('Product UoS'), compute='get_electric_counter', string="Compteur électrique")
    
    @api.depends('counter', 'electric_diff')
    def get_electric_counter(self):
        self.electric_counter = self.counter + self.electric_diff

class product_product(models.Model):
    _inherit = 'product.product'
    
    pumps = fields.One2many('stock.location.pump', 'product', string="Pompes")
    session_lines = fields.One2many('sale.session.line', 'product', string="Lignes de carburant")
