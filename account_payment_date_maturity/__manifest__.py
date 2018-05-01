# -*- coding: utf-8 -*-
{
    'name': "Account Payment Date Maturity",

    'summary': """
        Add Maturity date in account payments""",

    'description': """
        Add Maturity date in account payments in order to track checks.
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_payment.xml',
    ],
}