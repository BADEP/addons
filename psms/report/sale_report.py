# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 BADEP. All Rights Reserved.
#    Author: Khalid Hazam<k.hazam@badep.ma>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
 
from openerp.osv import fields, osv

class sale_report(osv.osv):
    _inherit = "sale.report"
    _columns = {
        'vehicle': fields.many2one('fleet.vehicle', 'Véhicule', readonly=True),
        'session': fields.many2one('sale.session', 'Session', readonly=True),
    }

    def _select(self):
        return  super(sale_report, self)._select() + ", s.vehicle, s.session"

    def _group_by(self):
        return super(sale_report, self)._group_by() + ", s.vehicle, s.session"

