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
from openerp import models, fields, api

class sale_order(models.Model):
    _inherit = 'sale.order'
    force_delivery = fields.Boolean(default = False)
    
    @api.multi
    def action_button_confirm(self):
        if super(sale_order,self).action_button_confirm():
            if self.force_delivery:
                for order in self:
                    for picking in order.picking_ids:
                        picking.action_confirm()
                        picking.force_assign()
                        picking.action_done()
        return True
    
sale_order()
