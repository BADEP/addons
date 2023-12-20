from odoo import api, models

class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        res = super()._prepare_purchase_order_line(po, item)
        if res:
            res.update({
                'dimension_ids': [(0, 0, {'dimension_id': d.dimension_id.id, 'quantity': d.quantity}) for d in item.line_id.dimension_ids]
            })
        return res

    @api.model
    def _get_order_line_search_domain(self, order, item):
        res = super()._get_order_line_search_domain(order, item)
        if item.line_id.dimension_ids:
            res.append(("purchase_request_lines", "in", [item.line_id.id]))
        return res