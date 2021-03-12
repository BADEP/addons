from odoo import models, fields, api

class sale_order(models.Model):
    _inherit = 'sale.order'

    vouchers_delivered = fields.One2many('sale.order.voucher', 'sale_order_delivered', readonly=True,
                                         states={'draft': [('readonly', False)]}, string="Bons d'échange donnés")
    vouchers_taken = fields.One2many('sale.order.voucher', 'sale_order_taken', readonly=True,
                                     states={'draft': [('readonly', False)]}, string="Bons d'échange reçus")
    delivery_order_ref = fields.Char(string="N° BL")

    def _amount_all(self):
        res = super(sale_order, self)._amount_all()
        for order in self:
            for vd in order.vouchers_delivered:
                res[order.id]['amount_untaxed'] += vd.price_total
                res[order.id]['amount_total'] += vd.price_total
            for vt in order.vouchers_taken:
                res[order.id]['amount_untaxed'] -= vt.price_total
                res[order.id]['amount_total'] -= vt.price_total
        return res


class sale_order_voucher(models.Model):
    _name = 'sale.order.voucher'

    sale_order_delivered = fields.Many2one('sale.order', required=True, string="Bon de commande de délivrance")
    sale_order_taken = fields.Many2one('sale.order', string="Bon de commande de consommation")
    name = fields.Char('Code', required=True)
    product = fields.Many2one('product.product', required=True, string="Article")
    quantity = fields.Float(digits_compute=dp.get_precision('Product UoS'), required=True, string="Quantité")
    uom = fields.Many2one('uom.uom', required=True, string="Unité de mesure")
    price_unit = fields.Float(digits_compute=dp.get_precision('Product Price'), required=True, string="Prix unitaire")
    price_total = fields.Float(digits_compute=dp.get_precision('Product Price'), compute='get_price_total',
                               string="Prix total")
    state = fields.Selection(
        [('draft', 'draft'), ('delivered', 'Delivered'), ('collected', 'Collected'), ('done', 'Done')], 'Etat',
        readonly=True, copy=False, select=True, default='draft')
    taxes = fields.Many2many('account.tax', string='Taxes', store=True)

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product:
            self.uom = self.product.uom_id
            warning_msgs = None
            if not self.sale_order_delivered.pricelist_id:
                warn_msg = _(
                    'You have to select a pricelist or a customer in the sales form ! Please set one before choosing a product.')
                warning_msgs = "No Pricelist ! : " + warn_msg + "\n\n"
            else:
                price = self.sale_order_delivered.pricelist_id.with_context(
                    uom=self.uom.id or self.product.uom_id.id, date=self.sale_order_delivered.date_order).price_get(
                    prod_id=self.product.id, qty=self.quantity or 1.0, partner=self.sale_order_delivered.partner_id.id)[
                    self.sale_order_delivered.pricelist_id.id]
                if price is False:
                    warn_msg = "Cannot find a pricelist line matching this product and quantity.\n" \
                               "You have to change either the product, the quantity or the pricelist."

                    warning_msgs += "No valid pricelist line found ! :" + warn_msg + "\n\n"
                else:
                    self.price_unit = price

    @api.depends('quantity', 'price_unit')
    def get_price_total(self):
        self.price_total = self.price_unit * self.quantity


class sale_order_old(models.Model):
    _inherit = 'sale.order'

    # def _get_order(self):
    #     result = {}
    #     for line in self.pool.get('sale.order.line').browse():
    #         result[line.order_id.id] = True
    #     return result.keys()

    # def _amount_all_wrapper(self):
    #     return self._amount_all()

    # def action_invoice_create(self, grouped=False, states=None, date_invoice=False):
    #     if states is None:
    #         states = ['confirmed', 'done', 'exception']
    #     res = False
    #     invoices = {}
    #     invoice_ids = []
    #     invoice = self.pool.get('account.move')
    #     obj_sale_order_line = self.pool.get('sale.order.line')
    #     partner_currency = {}
    #     # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
    #     # last day of the last month as invoice date
    #     if date_invoice:
    #         context = dict(date_invoice=date_invoice)
    #     for o in self:
    #         currency_id = o.pricelist_id.currency_id.id
    #         if (o.partner_id.id in partner_currency): #and (partner_currency[o.partner_id.id] <> currency_id):
    #             raise exceptions.UserError('You cannot group sales having different currencies for the same partner.')
    #
    #         partner_currency[o.partner_id.id] = currency_id
    #         lines = []
    #         for line in o.order_line:
    #             if line.invoiced:
    #                 continue
    #             elif (line.state in states):
    #                 lines.append(line.id)
    #         created_lines = obj_sale_order_line.invoice_line_create(lines)
    #         for vd in o.vouchers_delivered:
    #             vals = {
    #                 'name': vd.product.name,
    #                 'origin': vd.sale_order_delivered.name,
    #                 'account_id': vd.product.property_account_income.id if vd.product.property_account_income.id else vd.product.categ_id.property_account_income_categ.id,
    #                 'price_unit': vd.price_unit,
    #                 'quantity': vd.quantity,
    #                 'uos_id': vd.uom.id,
    #                 'product_id': vd.product.id or False,
    #                 'invoice_line_tax_id': [(6, 0, [x.id for x in vd.taxes])]
    #             }
    #             created_lines.append(self.pool.get('account.move.line').create(vals, context=context))
    #         for vt in o.vouchers_taken:
    #             vals = {
    #                 'name': vt.product.name,
    #                 'origin': vt.sale_order_taken.name,
    #                 'account_id': vt.product.property_account_income.id if vt.product.property_account_income.id else vt.product.categ_id.property_account_income_categ.id,
    #                 'price_unit': vt.price_unit,
    #                 'quantity':-vt.quantity,
    #                 'uos_id': vt.uom.id,
    #                 'product_id': vt.product.id or False,
    #                 'invoice_line_tax_id': [(6, 0, [x.id for x in vt.taxes])]
    #             }
    #             created_lines.append(self.pool.get('account.move.line').create(vals, context=context))
    #         if created_lines:
    #             invoices.setdefault(o.partner_invoice_id.id or o.partner_id.id, []).append((o, created_lines))
    #     if not invoices:
    #         for o in self.browse():
    #             for i in o.invoice_ids:
    #                 if i.state == 'draft':
    #                     return i.id
    #     for val in invoices.values():
    #         if grouped:
    #             res = self._make_invoice(val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
    #             invoice_ref = ''
    #             origin_ref = ''
    #             for o, l in val:
    #                 invoice_ref += (o.client_order_ref or o.name) + '|'
    #                 origin_ref += (o.origin or o.name) + '|'
    #                 self.write([o.id], {'state': 'progress'})
    #                 self.env.cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
    #                 self.invalidate_cache(['invoice_ids'], [o.id], context=context)
    #             # remove last '|' in invoice_ref
    #             if len(invoice_ref) >= 1:
    #                 invoice_ref = invoice_ref[:-1]
    #             if len(origin_ref) >= 1:
    #                 origin_ref = origin_ref[:-1]
    #             invoice.write([res], {'origin': origin_ref, 'name': invoice_ref})
    #         else:
    #             for order, il in val:
    #                 res = self._make_invoice(order, il, context=context)
    #                 invoice_ids.append(res)
    #                 self.write([order.id], {'state': 'progress'})
    #                 self.env.cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
    #                 self.invalidate_cache(['invoice_ids'], [order.id], context=context)
    #     return res
