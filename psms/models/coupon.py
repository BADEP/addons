from odoo import models, fields

class CouponProgram(models.Model):
    _inherit = 'coupon.program'
    _description = 'Inherited coupon'

    partner_id = fields.Many2one('res.partner', string="Client")
    discount_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount')], default="fixed_amount",
        help="Percentage - Entered percentage discount will be provided\n" +
        "Amount - Entered fixed amount discount will be provided")
    program_type = fields.Selection([
        ('promotion_program', 'Promotional Program'),
        ('coupon_program', 'Coupon Program'),
        ], default="coupon_program",
        help="""A promotional program can be either a limited promotional offer without code (applied automatically)
                or with a code (displayed on a magazine for example) that may generate a discount on the current
                order or create a coupon for a next order.

                A coupon program generates coupons with a code that can be used to generate a discount on the current
                order or create a coupon for a next order.""")


class CouponCoupon(models.Model):
    _inherit = 'coupon.coupon'

    amount = fields.Float(string="Montant")

    _sql_constraints = [
        ('unique_coupon_code', 'unique(id)', 'The coupon code must be unique!'),
    ]

    def create(self, vals):
        coupon = super(CouponCoupon,self).create(vals)

        if coupon.program_id.partner_id:
            coupon.write({'partner_id':coupon.program_id.partner_id})

        if coupon.program_id.discount_fixed_amount and len(coupon.program_id.pos_order_ids) == 0:
            coupon.write({'amount':coupon.program_id.discount_fixed_amount})
        return coupon

    def write(self, vals):
        cc = super().write(vals)

        if self.pos_order_id:
                    if self.amount > self.pos_order_id.amount_total:
                        self.env['coupon.coupon'].create({
                            'code': self.code,
                            'amount': self.amount-self.pos_order_id.amount_total,
                            'partner_id': self.partner_id.id,
                            'expiration_date': self.expiration_date,
                            'program_id': self.program_id.id
                        })

        return cc

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def create(self, vals):
        po = super(PosOrder, self).create(vals)
        for line in po.lines:

            if len(line.product_id.pump_ids) != 0 and line.product_id.lst_price != 0:
                line.write({'qty':line.price_unit/line.product_id.lst_price})

        return po