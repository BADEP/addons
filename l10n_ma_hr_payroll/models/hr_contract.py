from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    int1 = fields.Float(digits='Account', string="Indemnité Non taxable 1")
    int2 = fields.Float(digits='Account', string="Indemnité Non taxable 2")
    int3 = fields.Float(digits='Account', string="Indemnité Non taxable 3")
    int4 = fields.Float(digits='Account', string="Indemnité Non taxable 4")
    int5 = fields.Float(digits='Account', string="Indemnité Non taxable 5")
    it1 = fields.Float(digits='Account', string="Indemnité taxable 1")
    it2 = fields.Float(digits='Account', string="Indemnité taxable 2")
    it3 = fields.Float(digits='Account', string="Indemnité taxable 3")
    it4 = fields.Float(digits='Account', string="Indemnité taxable 4")
    it5 = fields.Float(digits='Account', string="Indemnité taxable 5")