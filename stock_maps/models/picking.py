# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import api, fields, models
from odoo.addons.base_geolocalize.models.res_partner import (
    geo_find, geo_query_address)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipping_longitude = fields.Float(string='Shipping Longitude', related='partner_id.partner_longitude',
                                      store=False, readonly=False, digits=(16, 5))
    shipping_latitude = fields.Float(string='Shipping Latitude', related='partner_id.partner_latitude',
                                     store=False, readonly=False, digits=(16, 5))

    def geo_localize(self):
        google_api_key = self.env['ir.config_parameter'].sudo().get_param(
            'google.api_key_geocode', default='')
        for picking in self.with_context(lang='en_US'):
            result = geo_find(
                addr=geo_query_address(
                    street=picking.partner_id.street,
                    zip=picking.partner_id.zip,
                    city=picking.partner_id.city,
                    state=picking.partner_id.state_id.name,
                    country=picking.partner_id.country_id.name),
                apikey=google_api_key)

            if result is None:
                result = geo_find(
                    addr=geo_query_address(
                        city=picking.partner_id.city,
                        state=picking.partner_id.state_id.name,
                        country=picking.partner_id.country_id.name),
                    apikey=google_api_key)

            if result:
                picking.write({
                    'shipping_latitude': result[0],
                    'shipping_longitude': result[1]
                })
        return True
