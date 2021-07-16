# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    vehicle_longitude = fields.Float(
        string='Longitude',
        digits=(16, 5))
    vehicle_latitude = fields.Float(
        string='Latitude',
        digits=(16, 5))

    @api.onchange('driver_id')
    def onchange_driver_id_geo(self):
        if self.driver_id:
            self.vehicle_latitude = self.driver_id.partner_latitude
            self.vehicle_longitude = self.driver_id.partner_longitude

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
        for vehicle in self.with_context(lang='en_US'):
            result = self._geo_localize(
                    street=vehicle.driver_id.street,
                    zip=vehicle.driver_id.zip,
                    city=vehicle.driver_id.city,
                    state=vehicle.driver_id.state_id.name,
                    country=vehicle.driver_id.country_id.name)

            if result:
                vehicle.write({
                    'shipping_latitude': result[0],
                    'shipping_longitude': result[1]
                })
        return True