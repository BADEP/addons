# -*- coding: utf-8 -*-
{
    'name': "Schedule email sending",

    'summary': """Schedule mail sent for a later date""",

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Discuss',
    'version': '13.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'web'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    # always loaded
    'data': [
        'views/mail_views.xml'
    ],
    'price': 29.00,
    'installable': True,
    'currency': 'EUR',
}