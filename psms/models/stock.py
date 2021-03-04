from odoo import models, fields

class StockLocationPump(models.Model):
    _name = 'stock.location.pump'
    _description = 'Pompe'
    
    location_id = fields.Many2one('stock.location', required=True, ondelete='cascade', string='Emplacement', domain=[('usage', '=', 'internal')])
    counter = fields.Float(digits='Product Unit Of Measure', required=True, default=0, string='Compteur')
    name = fields.Char(string='Nom')
    product_id = fields.Many2one('product.product', ondelete='set null', string='Article')
    log_ids = fields.One2many('pos.session.log', 'pump_id')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    pump_ids = fields.One2many('stock.location.pump', 'product_id', string='Pompes')