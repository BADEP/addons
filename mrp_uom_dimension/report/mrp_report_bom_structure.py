import json

from odoo import api, models, _
from odoo.tools import float_round

class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'
    _description = 'BOM Structure Report'

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        res = super(ReportBomStructure, self)._get_bom(bom_id, product_id, line_qty, line_id, level)
        # res['product_uom_qty'] = res['bom'] and res['bom']._get_product_dimension_qty() or ''
        # res['dimension_ids'] = res['bom'] and res['bom']._get_dimensions() or ''
        return res

    @api.model
    def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
        res = super()._get_report_data(bom_id, searchQty, searchVariant)
        bom = self.env['mrp.bom'].browse(bom_id)
        res.update({
            'dimensions':{
                d.id: d.name for d in bom.product_uom_id.dimension_ids
            }
        })
        return res

    def _get_dimensions_qty(self, bom_quantity, components):
        for line in components:
            bom_line = self.env['mrp.bom.line'].browse(line['line_id'])
            if bom_line.qty_type == 'fixed':
                if bom_line.dimension_ids:
                    line['product_dimension_qty'] = bom_line.product_dimension_qty
                    line['dimension_ids'] = {d.id: d.quantity for d in bom_line.dimension_ids}
            else:
                production_id = self.env.context.get('production_id', self.env['mrp.production'])
                eval_context = {
                    'env': self.env,
                    'context': self.env.context,
                    'user': self.env.user,
                    'production_id': production_id if production_id else False,
                    'line': bom_line,
                    'quantity': bom_quantity
                }
                line['prod_qty'] = bom_line.qty_formula_id.execute(eval_context)
                line_extra_data = bom_line.qty_formula_id.execute_extra_data(eval_context)
                if isinstance(line_extra_data, dict):
                    line.update(line_extra_data)
        return True

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components, total = super()._get_bom_lines(bom, bom_quantity, product, line_id, level)
        self._get_dimensions_qty(bom_quantity, components)
        return components, total

    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False):
        data = super(ReportBomStructure, self)._get_pdf_line(bom_id, product_id, qty, child_bom_ids, unfolded)
        self._get_dimensions_qty(data['lines'])
        return data
