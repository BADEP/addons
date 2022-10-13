from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_line_ids = fields.One2many('mrp.bom.line', 'bom_id', 'BoM Lines', domain= [('display_type', '=', False)], copy=False)
    bom_line_ids_with_sections = fields.One2many('mrp.bom.line', 'bom_id', 'BoM Lines', copy=True)

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    def _get_default_product_uom_id(self):
        return super()._get_default_product_uom_id()


    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Char()
    product_id = fields.Many2one('product.product', 'Component', required=False, check_company=True)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=False)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        default=_get_default_product_uom_id,
        required=False,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control", domain="[('category_id', '=', product_uom_category_id)]")