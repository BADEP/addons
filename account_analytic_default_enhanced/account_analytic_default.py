# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time

from openerp.osv import fields, osv


class account_analytic_default(osv.osv):
    _inherit = "account.analytic.default"
    _columns = {
        'section_id': fields.many2one('crm.case.section', 'Salesteam', ondelete='cascade', help="Select a salesteam which will use analytic account specified in analytic default."),
    }

    def account_get(self, cr, uid, product_id=None, partner_id=None, user_id=None, section_id=None, date=None, company_id=None, context=None):
        domain = []
        if product_id:
            domain += ['|', ('product_id', '=', product_id)]
        domain += [('product_id', '=', False)]
        if partner_id:
            domain += ['|', ('partner_id', '=', partner_id)]
        domain += [('partner_id', '=', False)]
        if company_id:
            domain += ['|', ('company_id', '=', company_id)]
        domain += [('company_id', '=', False)]
        if user_id:
            domain += ['|', ('user_id', '=', user_id)]
        domain += [('user_id', '=', False)]
        if section_id:
            section = self.pool.get('crm.case.section').browse(cr, uid, section_id, context=context)
            parent = section
            while parent:
                domain += ['|', ('section_id', '=', parent.id)]
                parent = parent.parent_id
        domain += [('section_id', '=', False)]
        if date:
            domain += ['|', ('date_start', '<=', date), ('date_start', '=', False)]
            domain += ['|', ('date_stop', '>=', date), ('date_stop', '=', False)]
        best_index = -1
        res = False
        for rec in self.browse(cr, uid, self.search(cr, uid, domain, context=context), context=context):
            index = 0
            if rec.product_id: index += 1
            if rec.partner_id: index += 1
            if rec.company_id: index += 1
            if rec.user_id: index += 1
            if rec.section_id: index += 1
            if rec.date_start: index += 1
            if rec.date_stop: index += 1
            if index > best_index:
                res = rec
                best_index = index
        return res

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        rec = self.pool.get('account.analytic.default').account_get(cr, uid, product_obj.id, partner_id, uid, partner.section_id.id, time.strftime('%Y-%m-%d'))
        if rec and rec.analytics_id:
            res['value'].update({'analytics_id': rec.analytics_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
