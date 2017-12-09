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
    'name': 'Sale Layout Colors',
    'version': '1.0',
    'category': 'Sales',
    'description': """
    Colors for Sale Sections: Add Field in Sale Section where the user can inputs the Hex Code for each section.
    """,
    'author': 'BADEP',
    'website': 'https://badep.ma',
    'depends': ['sale_layout',
                'web_widget_color'
                ],
    'data': [
           'views.xml',
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
