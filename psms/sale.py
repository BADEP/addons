# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class sale_session(models.Model):
    _name = 'sale.session'
    _description = 'Session'
    _inherit = 'mail.thread'
    
    _sql_constraints = [
        ('date_unique', 'unique(date)', 'Only 1 session per date is allowed!')
    ]
    
    @api.depends('date')
    def get_name(self):
        self.name = self.date
    
    def get_default_warehouse(self):
        return self.env.user.company_id.warehouse_ids[0].id if self.env.user.company_id.warehouse_ids else False
        
    date = fields.Date(default=fields.Date.today(), readonly=True, states={'draft': [('readonly', False)]})    
    sale_orders = fields.One2many('sale.order', 'session', readonly=True, states={'draft': [('readonly', False)]}, string="Bons de commande")
    name = fields.Char(string='Code', compute='get_name')
    responsable = fields.Many2one('hr.employee', required=True, domain="[('responsable','=','True')]", readonly=True, states={'draft': [('readonly', False)]})
    logs = fields.One2many('sale.session.log', 'session', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('except', 'Exception'), ('done', 'Done')], 'Etat', readonly=True, copy=False, select=True, default='draft')
    lines = fields.One2many('sale.session.line', 'session', string='Lignes de carburant')
    client_lines = fields.One2many('sale.session.client_line', 'session', string="Lignes par client")
    total_sales = fields.Float(digits_compute=dp.get_precision('Product Price'), compute='get_sales', string="Total des ventes")
    fuel_sales = fields.Float(digits_compute=dp.get_precision('Product Price'), compute='get_sales', string="Ventes carburant")
    other_sales = fields.Float(digits_compute=dp.get_precision('Product Price'), compute='get_sales', string="Ventes autre")
    warehouse = fields.Many2one('stock.warehouse', required=True, default=get_default_warehouse, readonly=True, states={'draft': [('readonly', False)]}, string="Entrepôt")
    note = fields.Text()

    def action_confirm(self):
        count = self.search_count([('state', '!=', 'done'), ('date', '<', self.date)])
        if count > 0:
            raise UserError('Une session antérieure est encore ouverte')
        for log in self.logs:
            if log.diff < 0:
                raise UserError('Log cannot be of a negative value')
        for line in self.lines:
            if abs(line.diff_qty) > 1:
                self.state = 'except'
                return False
        self.action_force()
        
    @api.onchange('logs')
    def update_line(self):
        for line in self.lines:
            log_qty = 0
            for log in self.logs:
                if log.pump.product.id == line.product.id:
                    log_qty += log.diff
            line.log_qty = log_qty
    
    def action_force(self):
        for order in self.sale_orders:
            order.date_order = self.date
            order.signal_workflow('order_confirm')
            for picking in order.picking_ids:
                picking.action_confirm()
                picking.force_assign()
                picking.action_done()
        for log in self.logs:
            log.pump.counter = log.new_counter
        self.state = 'done'

    @api.onchange('sale_orders')
    def get_client_lines(self):
        self.client_lines.unlink()
        self.client_lines = []
        partners = self.sale_orders.mapped('partner_id')
        for partner in partners:
            self.client_lines |= self.env['sale.session.client_line'].new({'partner': partner.id, 'session': self.id})

    @api.depends('sale_orders')
    def get_sales(self):
        other = 0
        total = 0
        fuel = 0
        for order in self.sale_orders:
            total += order.amount_total
            for line in order.order_line:
                if line.product_id.pumps:
                    fuel += line.price_total
                else:
                    other += line.price_total
        self.total_sales = total
        self.fuel_sales = fuel
        self.other_sales = other

    def action_import_data(self):
        count = self.search_count([('state', '!=', 'done'), ('date', '<', self.date)])
        if count > 0:
            UserError('Une session antérieure est encore ouverte')
        self.logs.unlink()
        self.write({'logs': [(0, 0, {'session': self.id, 'pump': x.id, 'old_counter': x.counter}) for x in self.env['stock.location.pump'].search([('location', 'child_of', self.warehouse.view_location_id.id)])]})
        self.sale_orders.write({'session': False})
        sale_orders = self.env['sale.order'].search([('session', '=', False), ('date_order', '>=', self.date)])
        self.write({'sale_orders': [(4, x.id) for x in sale_orders]})
        products = self.logs.mapped('pump.product')
        self.lines.unlink()
        self.write({'lines': [(0, 0, {'product': x.id, 'session': self.id}) for x in products]})
    
    @api.onchange('date')
    def onchange_date(self):
        self.lines.unlink()
        self.logs.unlink()
        self.sale_orders.unlink()

class sale_session_line(models.Model):
    _name = 'sale.session.line'
    _description = 'Ligne de carurant'
    
    product = fields.Many2one('product.product', readonly=True, string="Article")
    log_qty = fields.Float(digits_compute=dp.get_precision('Product UoS'), compute='get_log', string="Variance compteur")
    sale_qty = fields.Float(digits_compute=dp.get_precision('Product UoS'), compute='get_sales', string="Ventes")
    diff_qty = fields.Float(digits_compute=dp.get_precision('Product UoS'), compute='get_diff', string="Difference")
    session = fields.Many2one('sale.session', ondelete='cascade')
    
    @api.depends('session.sale_orders')
    def get_sales(self):
        sales = 0
        for order in self.session.sale_orders:
            for line in order.order_line:
                if line.product_id.id == self.product.id:
                    sales += line.product_uom_qty 
        self.sale_qty = sales

    @api.depends('log_qty', 'sale_qty')
    def get_diff(self):
        self.diff_qty = self.log_qty - self.sale_qty

    @api.depends('session.logs')
    def get_log(self):
        log_qty = 0
        for log in self.session.logs:
            if log.pump.product.id == self.product.id:
                log_qty += log.diff
        self.log_qty = log_qty

class sale_session_client_line(models.Model):
    _name = 'sale.session.client_line'
    _description = 'Ligne de vente client'
    
    partner = fields.Many2one('res.partner', readonly=True, string="Client")
    order_count = fields.Integer(compute='get_sales_and_count', string="Nombre de commandes")
    sale_qty = fields.Float(digits_compute=dp.get_precision('Product UoS'), compute='get_sales_and_count', string="Ventes")
    session = fields.Many2one('sale.session', ondelete='cascade')

    @api.depends('session.sale_orders')
    def get_sales_and_count(self):
        sales = 0
        count = 0
        for order in self.session.sale_orders:
            if order.partner_id.id == self.partner.id:
                sales += order.amount_total
                count += 1
        self.sale_qty = sales
        self.order_count = count

class sale_session_log(models.Model):
    _name = 'sale.session.log'
    _description = 'Log'
    
    session = fields.Many2one('sale.session', ondelete='cascade')
    pump = fields.Many2one('stock.location.pump', ondelete='cascade', string="Pompe")
    old_counter = fields.Float(digits_compute=dp.get_precision('Product UoS'), string="Ancien compteur")
    new_counter = fields.Float(digits_compute=dp.get_precision('Product UoS'), required=True, default=0, string="Nouveau compteur")
    diff = fields.Float(digits_compute=dp.get_precision('Product UoS'), compute='get_diff', string="Difference")
    electric_counter = fields.Float(digits_compute=dp.get_precision('Product UoS'), compute='get_electric_counter', string="Compteur électrique")

    @api.depends('new_counter', 'old_counter')
    def get_diff(self):
        self.diff = self.new_counter - self.old_counter

    @api.depends('new_counter')
    def get_electric_counter(self):
        self.electric_counter = self.new_counter + self.pump.electric_diff

class sale_order(models.Model):
    _inherit = 'sale.order'
    
    session = fields.Many2one('sale.session', ondelete='set null')
    vehicle = fields.Many2one('fleet.vehicle', ondelete='set null', string="Véhicule")
    vouchers_delivered = fields.One2many('sale.order.voucher', 'sale_order_delivered', readonly=True, states={'draft': [('readonly', False)]}, string="Bons d'échange donnés")
    vouchers_taken = fields.One2many('sale.order.voucher', 'sale_order_taken', readonly=True, states={'draft': [('readonly', False)]}, string="Bons d'échange reçus")
    delivery_order_ref = fields.Char(string="N° BL")

    def _amount_all(self, field_name, arg):
        res = super(sale_order, self)._amount_all(field_name, arg)
        for order in self:
            for vd in order.vouchers_delivered:
                res[order.id]['amount_untaxed'] += vd.price_total
                res[order.id]['amount_total'] += vd.price_total
            for vt in order.vouchers_taken:
                res[order.id]['amount_untaxed'] -= vt.price_total
                res[order.id]['amount_total'] -= vt.price_total
        return res
        
class sale_order_old(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'
    
    def onchange_partner_id(self):
        val = super(sale_order, self).onchange_partner_id()
        val['value'].update({'vehicle': False})
        return val
    
    def _get_order(self):
        result = {}
        for line in self.pool.get('sale.order.line').browse():
            result[line.order_id.id] = True
        return result.keys()
    
    def _amount_all_wrapper(self):
        return self._amount_all()

    amount_untaxed = fields.Float(string='Untaxed Amount')
    amount_tax = fields.Float(string='Taxes')
    amount_total = fields.Float(string='Total')
    
    # _columns = {
    #     'amount_untaxed': oldfields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
    #         store={
    #             'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'vouchers_delivered', 'vouchers_taken'], 10),
    #             'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
    #         },
    #         multi='sums', help="The amount without tax.", track_visibility='always'),
    #     'amount_tax': oldfields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Taxes',
    #         store={
    #             'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'vouchers_delivered', 'vouchers_taken'], 10),
    #             'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
    #         },
    #         multi='sums', help="The tax amount."),
    #     'amount_total': oldfields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Total',
    #         store={
    #             'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'vouchers_delivered', 'vouchers_taken'], 10),
    #             'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
    #         },
    #         multi='sums', help="The total amount.")
    # }
    
    def action_invoice_create(self, grouped=False, states=None, date_invoice=False):
        if states is None:
            states = ['confirmed', 'done', 'exception']
        res = False
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.move')
        obj_sale_order_line = self.pool.get('sale.order.line')
        partner_currency = {}
        # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
        # last day of the last month as invoice date
        if date_invoice:
            context = dict(date_invoice=date_invoice)
        for o in self.browse():
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency): #and (partner_currency[o.partner_id.id] <> currency_id):
                raise exceptions.UserError('You cannot group sales having different currencies for the same partner.')

            partner_currency[o.partner_id.id] = currency_id
            lines = []
            for line in o.order_line:
                if line.invoiced:
                    continue
                elif (line.state in states):
                    lines.append(line.id)
            created_lines = obj_sale_order_line.invoice_line_create(lines)
            for vd in o.vouchers_delivered:
                vals = {
                    'name': vd.product.name,
                    'origin': vd.sale_order_delivered.name,
                    'account_id': vd.product.property_account_income.id if vd.product.property_account_income.id else vd.product.categ_id.property_account_income_categ.id,
                    'price_unit': vd.price_unit,
                    'quantity': vd.quantity,
                    'uos_id': vd.uom.id,
                    'product_id': vd.product.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in vd.taxes])]
                }
                created_lines.append(self.pool.get('account.move.line').create(vals, context=context))
            for vt in o.vouchers_taken:
                vals = {
                    'name': vt.product.name,
                    'origin': vt.sale_order_taken.name,
                    'account_id': vt.product.property_account_income.id if vt.product.property_account_income.id else vt.product.categ_id.property_account_income_categ.id,
                    'price_unit': vt.price_unit,
                    'quantity':-vt.quantity,
                    'uos_id': vt.uom.id,
                    'product_id': vt.product.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in vt.taxes])]
                }
                created_lines.append(self.pool.get('account.move.line').create(vals, context=context))
            if created_lines:
                invoices.setdefault(o.partner_invoice_id.id or o.partner_id.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse():
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            if grouped:
                res = self._make_invoice(val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
                invoice_ref = ''
                origin_ref = ''
                for o, l in val:
                    invoice_ref += (o.client_order_ref or o.name) + '|'
                    origin_ref += (o.origin or o.name) + '|'
                    self.write([o.id], {'state': 'progress'})
                    self.env.cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
                    self.invalidate_cache(['invoice_ids'], [o.id], context=context)
                # remove last '|' in invoice_ref
                if len(invoice_ref) >= 1:
                    invoice_ref = invoice_ref[:-1]
                if len(origin_ref) >= 1:
                    origin_ref = origin_ref[:-1]
                invoice.write([res], {'origin': origin_ref, 'name': invoice_ref})
            else:
                for order, il in val:
                    res = self._make_invoice(order, il, context=context)
                    invoice_ids.append(res)
                    self.write([order.id], {'state': 'progress'})
                    self.env.cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
                    self.invalidate_cache(['invoice_ids'], [order.id], context=context)
        return res

class sale_order_voucher(models.Model):
    _name = 'sale.order.voucher'
    
    sale_order_delivered = fields.Many2one('sale.order', required=True, string="Bon de commande de délivrance")
    sale_order_taken = fields.Many2one('sale.order', string="Bon de commande de consommation")
    name = fields.Char('Code', required=True)
    product = fields.Many2one('product.product', required=True, string="Article")
    quantity = fields.Float(digits_compute=dp.get_precision('Product UoS'), required=True, string="Quantité")
    uom = fields.Many2one('product.uom', required=True, string="Unité de mesure")
    price_unit = fields.Float(digits_compute=dp.get_precision('Product Price'), required=True, string="Prix unitaire")
    price_total = fields.Float(digits_compute=dp.get_precision('Product Price'), compute='get_price_total', string="Prix total")
    state = fields.Selection([('draft', 'draft'), ('delivered', 'Delivered'), ('collected', 'Collected'), ('done', 'Done')], 'Etat', readonly=True, copy=False, select=True, default='draft')
    taxes = fields.Many2many('account.tax', string='Taxes', related='product.taxes_id', store=True)

    @api.onchange('product')
    def onchange_product(self):
        if self.product:
            self.uom = self.product.uom_id
            if not self.sale_order_delivered.pricelist_id:
                warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                        'Please set one before choosing a product.')
                warning_msgs = "No Pricelist ! : " + warn_msg + "\n\n"
            else:
                price = self.sale_order_delivered.pricelist_id.with_context(
                    uom=self.uom.id or self.product.uom_id.id, date=self.sale_order_delivered.date_order).price_get(
                    prod_id=self.product.id, qty=self.quantity or 1.0, partner=self.sale_order_delivered.partner_id.id)[self.sale_order_delivered.pricelist_id.id]
                if price is False:
                    warn_msg = "Cannot find a pricelist line matching this product and quantity.\n" \
                            "You have to change either the product, the quantity or the pricelist."
    
                    warning_msgs += "No valid pricelist line found ! :" + warn_msg + "\n\n"
                else:
                    self.price_unit = price

    @api.depends('quantity', 'price_unit')
    def get_price_total(self):
        self.price_total = self.price_unit * self.quantity
    
class hr_employee(models.Model):
    _inherit = 'hr.employee'
    responsable = fields.Boolean(default=False)

# class sale_make_invoice(models.TransientModel):
#     _inherit = 'sale.make.invoice'
#
#     def make_invoices(self):
#         result = super(sale_make_invoice, self).make_invoices()
#         if self.grouped:
#             orders = self.env['sale.order'].browse(self.env.context.get(('active_ids'), []))
#             for o in orders:
#                 for i in o.invoice_ids:
#                     i.merge_lines()
#             return result

class res_partner(models.Model):
    _inherit = 'res.partner'

    def name_get(self):
        res = []
        for rec in self:       
            if rec.ref:
                res.append((rec.id, '[%s] %s' % (rec.ref, rec.name)))
            else:
                res.append((rec.id, rec.name))
        return res
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        args = args[:]
        recs = []
        if name:
            recs = self.search([('ref', operator, name)] + args, limit=limit) | self.search([('name', operator, name)] + args, limit=limit)
        else:
            recs = self.search(args, limit=limit)
        return recs.name_get()