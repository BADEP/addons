# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2016-2016 BADEP. All Rights Reserved.
#    Author: Khalid HAZAM <k.hazam@badep.ma>
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
    'name': 'Petrostar Customization',
    'version': '1.0',
    'category': 'Sales',
    'description': """
    Petrostar meta-package
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['account_accountant',
                'purchase',
                'sale_stock',
                'stock_account',
                'fleet',
                'sale_transport_multi_address',
                'stock_transport_multi_address',
                'purchase_transport_multi_address'
                ],
    'data': [
           'views.xml',
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
