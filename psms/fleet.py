# -*- coding: utf-8 -*-

from odoo import models, fields

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    partner = fields.Many2one('res.partner', ondelete='set null', string="Partenaire")

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    vehicles = fields.One2many('fleet.vehicle', 'partner', string="Véhicules")
