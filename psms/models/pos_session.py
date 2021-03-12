from odoo import models, fields, api

class PosSession(models.Model):
    _inherit = 'pos.session'

    log_ids = fields.One2many('pos.session.log', 'session_id')
    line_ids = fields.One2many('pos.session.line', 'session_id', string='Lignes de carburant')
    client_line_ids = fields.One2many('pos.session.client_line', 'session_id', compute='get_client_lines', string="Lignes par client")
    total_sales = fields.Monetary(compute='get_sales', string="Espéces")
    fuel_sales = fields.Monetary(compute='get_sales', string="Total des ventes")
    other_sales = fields.Monetary(compute='get_sales', string="Bons d'changes")
    #used_coupon_ids = fields.Many2many('coupon.coupon', compute='get_used_coupons')
    #generated_coupon_ids = fields.Many2many('coupon.coupon', compute='get_used_coupons')
    payment_bon_ids = fields.Many2many('pos.payment', compute='get_bon_payment')

    @api.depends('order_ids')
    def get_bon_payment(self):
        for rec in self:
            rec.payment_bon_ids = rec.order_ids.mapped('payment_ids').filtered(lambda p: p.payment_method_id.name == 'Bon')

    #@api.depends('order_ids')
    #def get_used_coupons(self):
    #    for rec in self:
    #        rec.used_coupon_ids = rec.order_ids.mapped('used_coupon_ids')
    #        rec.generated_coupon_ids = rec.order_ids.mapped('generated_coupon_ids')

    # def action_confirm(self):
    #     count = self.search_count([('state', '!=', 'done'), ('date', '<', self.date)])
    #     if count > 0:
    #         raise UserError('Une session antérieure est encore ouverte')
    #     for log in self.logs:
    #         if log.diff < 0:
    #             raise UserError('Log cannot be of a negative value')
    #     for line in self.lines:
    #         if abs(line.diff_qty) > 1:
    #             self.state = 'except'
    #             return False
    #     self.state = 'done'

    @api.onchange('log_ids')
    def update_line(self):
        for line in self.line_ids:
            log_qty = 0
            for log in self.log_ids:
                if log.pump_id.product_id.id == line.product_id.id:
                    log_qty += log.diff
            line.log_qty = log_qty

    # todo: replace by session closing
    def action_pos_session_closing_control(self):
        for log in self.log_ids:
            log.pump_id.counter = log.new_counter
        return super().action_pos_session_closing_control()

    @api.depends('order_ids')
    def get_client_lines(self):
        self.client_line_ids.unlink()
        partners = self.order_ids.mapped('partner_id')
        for partner in partners:
            self.client_line_ids |= self.env['pos.session.client_line'].new({'partner_id': partner.id, 'session_id': self.id})


    @api.depends('order_ids')
    def get_sales(self):

        other = 0
        total = 0
        fuel = 0
        for order in self.order_ids:
            total += order.amount_total
            for line in order.lines:
                if len(line.product_id.pump_ids) != 0:
                    fuel += line.price_subtotal_incl
                else:
                    other += line.price_subtotal_incl
        self.fuel_sales = fuel
        self.other_sales = sum(l.amount for l in self.payment_bon_ids)
        self.total_sales = self.fuel_sales - self.other_sales

    def action_import_data(self):
        self.log_ids.unlink()
        self.write({'log_ids': [(0, 0, {'session_id': self.id, 'pump_id': x.id, 'old_counter': x.counter}) for x in
                                self.env['stock.location.pump'].search(
                                    [('location_id', 'child_of', self.config_id.picking_type_id.default_location_src_id.id)])]})
        products = self.log_ids.mapped('pump_id.product_id')
        self.line_ids.unlink()
        self.write({'line_ids': [(0, 0, {'product_id': x.id, 'session_id': self.id}) for x in products]})

class PosSessionLine(models.Model):
    _name = 'pos.session.line'
    _description = 'Ligne de carburant'

    product_id = fields.Many2one('product.product', readonly=True, string="Article")
    log_qty = fields.Float(digits='Product Unit Of Measure', compute='get_log', string="Variance compteur")
    sale_qty = fields.Float(digits='Product Unit Of Measure', compute='get_sales', string='Ventes')
    diff_qty = fields.Float(digits='Product Unit Of Measure', compute='get_diff', string='Différence')
    session_id = fields.Many2one('pos.session', ondelete='cascade')

    @api.depends('session_id.order_ids')
    def get_sales(self):
        sales = 0
        for rec in self:
            rec.sale_qty = sum(rec.session_id.order_ids.mapped('lines').filtered(lambda l: l.product_id == rec.product_id).mapped('qty'))

    @api.depends('log_qty', 'sale_qty')
    def get_diff(self):
        for rec in self:
            rec.diff_qty = rec.log_qty - (rec.sale_qty+(5/1000))

    @api.depends('session_id.log_ids')
    def get_log(self):
        for rec in self:
            rec.log_qty = sum(rec.session_id.log_ids.filtered(lambda l: l.pump_id.product_id == rec.product_id).mapped('diff'))

class PosSessionClientLine(models.Model):
    _name = 'pos.session.client_line'
    _description = 'Ligne de vente client'

    session_id = fields.Many2one('pos.session', ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='session_id.currency_id')
    partner_id = fields.Many2one('res.partner', readonly=True, string="Client")
    order_count = fields.Integer(compute='get_sales_and_count', string="Nombre de commandes")
    sale_amount = fields.Monetary(currency_field='currency_id', compute='get_sales_and_count', string="Ventes")

    @api.depends('session_id.order_ids')
    def get_sales_and_count(self):
        for rec in self:
            rec.sale_qty = sum(rec.session_id.order_ids.filtered(lambda o: o.partner_id == rec.partner_id).mapped('amount_total'))
            rec.order_count = len(rec.session_id.order_ids.filtered(lambda o: o.partner_id == rec.partner_id))

class PosSessionLog(models.Model):
    _name = 'pos.session.log'
    _description = 'Log'

    session_id = fields.Many2one('pos.session', ondelete='cascade')
    pump_id = fields.Many2one('stock.location.pump', ondelete='cascade', string="Pompe")
    old_counter = fields.Float(digits='Product Unit Of Measure', string="Ancien compteur")
    new_counter = fields.Float(digits='Product Unit Of Measure', required=True, default=0, string="Nouveau compteur")
    diff = fields.Float(digits='Product Unit Of Measure', compute='get_diff', string="Difference", store=True)

    @api.depends('new_counter', 'old_counter')
    def get_diff(self):
        for rec in self:
            rec.diff = rec.new_counter - rec.old_counter