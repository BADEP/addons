from odoo import models, fields, api, exceptions, _
from datetime import datetime

class SaleMeasure(models.Model):
    _name = "sale.measure"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'sale_order_id'
    _description = 'OPM'

    sale_order_id = fields.Many2one('sale.order', string='Bon de commande')
    user_id = fields.Many2one('res.users', string="Responsable mesures")
    measure_start = fields.Datetime(string="Date de début de mesure")
    measure_end = fields.Datetime(string="Date de fin de mesure")
    partner_id = fields.Many2one('res.partner', related='sale_order_id.partner_shipping_id', string="Client",
                                 readonly=True)
    sale_order_line_ids = fields.Many2many('sale.order.line', string="Ligne BC", compute='get_sale_order_line_ids')
    shipping_longitude = fields.Float(string='Shipping Longitude', compute='get_location_data', inverse='inverse_location_data',
                                      store=False, digits=(16, 5))
    shipping_latitude = fields.Float(string='Shipping Latitude', compute='get_location_data', inverse='inverse_location_data',
                                     store=False, digits=(16, 5))
    measure_ids = fields.One2many('sale.measure.line', 'measure_id', copy=True)
    notes = fields.Html()
    state = fields.Selection([('draft', 'Brouillon'), ('done', 'Fait')], default='draft')

    @api.depends('partner_id')
    def get_location_data(self):
        for rec in self:
            rec.shipping_longitude = rec.partner_id.partner_longitude
            rec.shipping_latitude = rec.partner_id.partner_latitude


    @api.depends('shipping_longitude', 'shipping_latitude')
    def inverse_location_data(self):
        for rec in self:
            rec.partner_id.sudo().write({'partner_longitude': rec.shipping_longitude, 'partner_latitude': rec.shipping_latitude})

    def action_done(self):
        for rec in self:
            rec.measure_ids.action_done()
            rec.write({'state': 'done'})

    @api.depends('measure_ids')
    def get_sale_order_line_ids(self):
        for rec in self:
            rec.sale_order_line_ids = rec.measure_ids.mapped('sale_order_line_id')

class SaleMeasureLine(models.Model):
    _name = "sale.measure.line"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'sale_order_line_id'
    _description = 'OPM Line'

    code = fields.Char(string="Repère")
    piece = fields.Char(string="Pièce")
    user_id = fields.Many2one('res.users', string="Responsable mesures", default=lambda self: self.env.user)
    measure_date = fields.Date(string="Date de mesure", default=fields.Date.today)
    state = fields.Selection([('draft', 'Brouillon'), ('done', 'Fait')], default='draft')
    dimension_ids = fields.One2many('sale.measure.line.dimension', 'measure_id')
    measure_id = fields.Many2one('sale.measure', ondelete='cascade')
    ouverture = fields.Selection([
        ('A', 'Droit intérieur'),
        ('B', 'Droit extérieur'),
        ('C', 'Gauche intérieur'),
        ('D', 'Gauche extérieur'),
    ], string="Ouverture")
    sale_order_line_id = fields.Many2one('sale.order.line', string="Ligne BC", readonly=True)
    product_id = fields.Many2one('product.product', related='sale_order_line_id.product_id', string='Article')
    notes = fields.Html()
    margin = fields.Float('Dépassement (%)', compute='compute_margin')

    def action_done(self):
        for rec in self:
            if not rec.code:
                raise exceptions.ValidationError("Veuillez remplir le champ code")
            if not rec.piece:
                raise exceptions.ValidationError("Veuillez remplir le champ piece")
            for line in rec.dimension_ids:
                if line.quantity == 0:
                    raise exceptions.ValidationError("Veuillez remplir la dimension %s" % (
                        line.dimension_id.name))
            rec.process_margin()
            location = rec.env.context.get('location', False)
            if location:
                rec.mapped('measure_id').write({
                    'shipping_latitude': location[0],
                    'shipping_longitude': location[1],
                })
            rec.write({'state': 'done'})
            if all(ml.state == 'done' for ml in rec.measure_id.measure_ids):
                rec.measure_id.write({'state': 'done'})

    @api.depends('dimension_ids.margin')
    def compute_margin(self):
        for rec in self:
            rec.margin = rec.dimension_ids and max(rec.dimension_ids.mapped('margin')) or 0

    def process_margin(self):
        for ml in self.sudo():
            rec = ml.sale_order_line_id
            if abs(ml.margin) > 10:
                if rec.product_dimension_qty == 1:
                    rec.dimension_ids.unlink()
                    rec.write({
                        'price_to_update': True,
                        'dimension_ids': [(0, 0, {
                            'dimension_id': d.dimension_id.id,
                            'quantity': d.quantity
                        }) for d in ml.dimension_ids],
                    })
                else:
                    new_rec = rec.order_id.order_line.filtered(
                        lambda sol: sol.product_id == ml.product_id and sol.dimension_ids.mapped(
                            'quantity') == ml.dimension_ids.mapped('quantity'))
                    if new_rec:
                        new_rec.write({
                            'product_dimension_qty': new_rec.product_dimension_qty + 1,
                            'price_to_update': True
                        })
                    else:
                        new_rec = rec.copy({
                            'price_to_update': True,
                            'order_id': rec.order_id.id,
                            'dimension_ids': [(0, 0, {
                                'dimension_id': d.dimension_id.id,
                                'quantity': d.quantity
                            }) for d in ml.dimension_ids],
                            'product_dimension_qty': 1,
                        })
                    ml.write({
                        'sale_order_line_id': new_rec.id
                    })
                    rec.product_dimension_qty -= 1
                    new_rec.onchange_dimension_ids()
                for dimension in ml.dimension_ids:
                    dimension.write({'expected_quantity': dimension.quantity})
                rec.onchange_dimension_ids()
                rec.order_id.activity_schedule(
                    'sale.mail_act_sale_upsell',
                    user_id=rec.order_id.user_id.id,
                    note=_(
                        "Mettre à jour le prix de <a href='#' data-oe-model='%s' data-oe-id='%d'>%s</a> pour le client <a href='#' data-oe-model='%s' data-oe-id='%s'>%s</a>") % (
                             rec.order_id._name, rec.order_id.id, rec.name,
                             rec.order_id.partner_id._name, rec.order_id.partner_id.id,
                             rec.order_id.partner_id.display_name))

class SaleMeasureLineDimension(models.Model):
    _name = 'sale.measure.line.dimension'
    _description = 'Measure Line Dimension'

    dimension_id = fields.Many2one('uom.dimension', readonly=True, required=True, ondelete='cascade')
    quantity = fields.Float('Relevé', required=True)
    expected_quantity = fields.Float('Prévu', readonly=True)
    margin = fields.Float('Dépassement (%)', compute='compute_margin')
    measure_id = fields.Many2one('sale.measure.line', readonly=True, required=True, ondelete='cascade')
    name = fields.Char(compute='get_name', store=False)
    display_name = fields.Char(compute='get_name', store=False)

    @api.depends('expected_quantity', 'quantity')
    def compute_margin(self):
        for rec in self:
            if rec.quantity != 0 and rec.expected_quantity != 0:
                rec.margin = round((rec.quantity - rec.expected_quantity) / rec.expected_quantity, 3) * 100
            else:
                rec.margin = 0

    @api.depends('dimension_id', 'quantity')
    def get_name(self):
        for rec in self.filtered(lambda d: d.dimension_id):
            rec.display_name = rec.dimension_id.name + ': ' + (str(rec.quantity) if rec.quantity else str(rec.expected_quantity) + '*')
            rec.name = rec.dimension_id.name + ': ' + (str(rec.quantity) if rec.quantity else str(rec.expected_quantity) + '*')
