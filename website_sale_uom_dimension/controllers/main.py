import json

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleDimensions(WebsiteSale):

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        res = super().cart_update(product_id, add_qty, set_qty, **kw)
        sale_order = request.website.sale_get_order(force_create=True)
        order_line = sale_order._cart_find_product_line(int(product_id), line_id = False, **kw)[:1]
        if order_line and order_line.product_uom.dimension_ids and kw.get('dimension_values'):
            dimension_values = json.loads(kw['dimension_values'])
            order_line.dimension_ids.unlink()
            vals = {
                'dimension_ids': [(0, 0, {'dimension_id': d['dimension_id'], 'quantity': float(d['quantity'])}) for d in dimension_values],
                'product_dimension_qty': add_qty
            }
            order_line.write(vals)
            order_line.onchange_dimension_ids()
        return res