# -*- coding: utf-8 -*-
{
    'name': "Num2words support for currency",

    'summary': """Add support to call num2words (amount to text) directly from res_currency just like Odoo 11.0
        """,

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '10.0.1',
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    "external_dependencies": {"python" : ["num2words"]},
    # always loaded
    'data': [
        'views/res_currency.xml'
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
}