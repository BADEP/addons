# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import api, fields, models
from odoo.addons.base_geolocalize.models.res_partner import (
    geo_find, geo_query_address)


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

    def geo_localize(self):
        google_api_key = self.env['ir.config_parameter'].sudo().get_param(
            'google.api_key_geocode', default='')
        for vehicle in self.with_context(lang='en_US').filtered(lambda v: v.location):
            result = geo_find(
                addr=vehicle.location,
                apikey=google_api_key)

            if result:
                vehicle.write({
                    'vehicle_latitude': result[0],
                    'vehicle_longitude': result[1]
                })
        return True
