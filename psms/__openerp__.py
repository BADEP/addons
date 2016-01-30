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


{
    'name': 'Petrol Station Management System',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['stock', 'product', 'sale', 'purchase', 'mail', 'base', 'fleet', 'sale_taxed_total', 'hr', 'account_invoice_merge_lines', 'amount_to_text_fr'],
    'data': ['account_view.xml', 'product_view.xml', 'sale_view.xml', 'fleet_view.xml', 'report/sale_report_view.xml', 'report/account_invoice_report_view.xml', 'security/ir.model.access.csv'],
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
