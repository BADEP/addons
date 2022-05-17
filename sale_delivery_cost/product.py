# -*- coding: utf-8 -*-

from odoo import fields, models



class product_template(models.Model):
    _inherit = 'product.template'
    
    delivery_costs = fields.One2many('product.delivery.cost', 'product', string="Coûts de livraison")

class product_delivery_cost(models.Model):
    _name = 'product.delivery.cost'
    _description = 'Coût de livraison'

    code = fields.Many2one('product.delivery.code', ondelete='cascade', string='Tarif DT')
    price = fields.Float(required=True, digits='Product Price', default=0, string='Prix transport')
    product = fields.Many2one('product.template', ondelete='cascade', string='Article')
    pricelist = fields.Many2one('product.pricelist', ondelete='set null')

class product_delivery_code(models.Model):
    _name = 'product.delivery.code'
    _description = 'Tarif DT'

    name = fields.Char(required=True, string='Label')
    partners = fields.One2many('res.partner', 'code', string='Clients')
    delivery_costs = fields.One2many('product.delivery.cost', 'code', string='DT')

