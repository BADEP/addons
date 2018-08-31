# -*- coding: utf-8 -*-
{
    'name': "Purchase Responsible",

    'summary': """
        Set purchase responsible field""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '10.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_view.xml',
    ],
    "installable": False
}