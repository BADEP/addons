# -*- coding: utf-8 -*-
from odoo import models, fields

class sale_report(models.Model):
    _inherit = "sale.report"

    vehicle = fields.Many2one('fleet.vehicle', 'Véhicule', readonly=True)
    session = fields.Many2one('sale.session', 'Session', readonly=True)

    def _select(self):
        return  super(sale_report, self)._select() + ", s.vehicle, s.session"

    def _group_by(self):
        return super(sale_report, self)._group_by() + ", s.vehicle, s.session"

