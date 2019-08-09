# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 rhfree (<http://rhfree.com>).
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
    'name': 'Morocco-payroll Basic',
    'category': 'Human Resources',
    'author': 'rhfree.com',
    'website': 'http://rhfree.com',
    "license": "AGPL-3",
    'version': '1.3Basic',
    'depends': ['hr_payroll'],
    
	
    'description': """Moroccan Payroll Rules Basic Version.
======================

    - Configuration of hr_payroll for Moroccan localization
    - Basic configuration for newly installed company
    - Absence - Advances - CNSS - AMO
	- Pro version is complete and  handles all kinds of allowances and Bonuses, plus 
	        - Seniority ( anciennété) and all other advantages:
        	- CIMR and private health insurance like  AXA 
			- Nice looking payslip
			- Legal reports ( etat 9421 ) ...
    - Important: you need to fill the wage amount for the employee in the contract and chose moroccan payroll from the structure field.
    """,
    'data': [
        'data/l10n_ma_hr_payroll_data.xml',
        'views/l10n_ma_hr_payroll_view.xml',

    ],
	 'installable': True,
     "images":['static/description/Banner.png'],
}
