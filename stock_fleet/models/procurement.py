# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'
    vehicle = fields.Many2one('fleet.vehicle', domain=[('picking_ok','=',True)])
    driver = fields.Many2one('res.partner')