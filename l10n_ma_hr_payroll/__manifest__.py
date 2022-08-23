# -*- encoding: utf-8 -*-
{
    'name': 'Paie - Maroc',
    'category': 'Human Resources',
    'author': 'BADEP, rhfree.com',
    'website': 'https://badep.ma, http://rhfree.com',
    "license": "AGPL-3",
    "version": "14.0.2",
    'depends': ['hr_payroll_community'],

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
        'views/hr_contract_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payslip_views.xml',
        'views/res_company_views.xml',
        'report/report_paie.xml',
    ],
     'installable': True,
     "images":['static/description/Banner.png'],
}
