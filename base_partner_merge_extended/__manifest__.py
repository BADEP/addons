# -*- coding: utf-8 -*-
{
    'name': "Merge partners by additionnal fields",

    'summary': """
        Add phone and mobile on the merge partner wizard""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    # always loaded
    'data': [
        'wizard/base_partner_merge_views.xml',
    ],
    'price': 19.00,
    'currency': 'EUR',
}