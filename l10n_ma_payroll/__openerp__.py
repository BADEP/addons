# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015 Odoo SA (<http://odoo.com>).
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
    'name': 'Morocco-payroll',
    'category': 'Localization/Payroll',
    'author': 'Said Hijaoui (rhfree)',
    'website': 'http://rhfree.com',
    "category" : "Localization",
    'version': '1.0Basic',
    'depends': ['hr_payroll'],
    
	
    'description': """Moroccan Payroll Rules Basic Version.
======================

    - Configuration of hr_payroll for Moroccan localization
    - Basic configuration for newly installed company'
    - Absence - Advances - CNSS - AMO
	- Allow to split  Last name and First name in the contract
	- Pro version  handles all kinds of allowances and bonuses plus seniority and other advantages like CIMR and private health insurance 
    """,
    'active': False,
    'update_xml':['l10n_ma_payroll_view.xml'],
	 'data': [
        'l10n_ma_payroll_view.xml',
        'l10n_ma_payroll_data.xml',
		'views/payslip_report_view.xml',
        'l10n_ma_payroll_reports.xml',
        
       ],
    'auto_install': False,
    'installable': True,
    'application': False,
	
}
