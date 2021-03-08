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

class CouponCoupon(models.Model):
    _inherit = 'coupon.coupon'

    consumed_amount = fields.Float(string="Montant Consommé ")
    remaining_amount = fields.Float(string="Montant Restant")

    def create(self, vals):
        coupon = super(CouponCoupon,self).create(vals)
        if coupon.program_id.partner_id:
            coupon.write({'partner_id':coupon.program_id.partner_id})
        return coupon

