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
    'name': 'Consignation',
    'version': '1.0',
    'category': 'Warehouse Management',
    'description': """
    Consignation module for Coca-cola.
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['stock', 'sale_stock', 'point_of_sale', 'purchase', 'account_invoice_merge', 'product_bundle'],
    'data': [
           'account_view.xml',
           'product_view.xml',
           'delivery_view.xml',
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
