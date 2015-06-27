from openerp import fields, models

class product_template(models.Model):
    _inherit = 'product.template'
    city_from = fields.Many2one('res.country.state.city', ondelete="set null")
    city_to = fields.Many2one('res.country.state.city', ondelete="set null")
product_template()

class transport_grid(models.Model):
    _name = 'transport.grid'
    
    name = fields.Char(string='Description')
    city_from = fields.Many2one('res.country.state.city', required=True)
    city_to = fields.Many2one('res.country.state.city', required=True)
    time = fields.Float(required=True)
    distance = fields.Float(required=True)
transport_grid()