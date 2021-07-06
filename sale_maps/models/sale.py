from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_longitude = fields.Float(string='Shipping Longitude', related='partner_shipping_id.partner_longitude',
                                      store=False, readonly=False, digits=(16, 5))
    shipping_latitude = fields.Float(string='Shipping Latitude', related='partner_shipping_id.partner_latitude',
                                     store=False, readonly=False, digits=(16, 5))

    @api.model
    def _geo_localize(self, street='', zip='', city='', state='', country=''):
        geo_obj = self.env['base.geocoder']
        search = geo_obj.geo_query_address(
            street=street, zip=zip, city=city, state=state, country=country
        )
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(
                city=city, state=state, country=country
            )
            result = geo_obj.geo_find(search, force_country=country)
        return result


    def geo_localize(self):
        for sale in self.with_context(lang='en_US'):
            result = self._geo_localize(
                    street=sale.partner_shipping_id.street,
                    zip=sale.partner_shipping_id.zip,
                    city=sale.partner_shipping_id.city,
                    state=sale.partner_shipping_id.state_id.name,
                    country=sale.partner_shipping_id.country_id.name)

            if result:
                sale.write({
                    'shipping_latitude': result[0],
                    'shipping_longitude': result[1]
                })
        return True
