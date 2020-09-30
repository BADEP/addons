# -*- coding: utf-8 -*-
{
    'name': "Purchase Vendor Pricelist",

    'summary': """
        Display a form for list prices in vendor""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '14.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['product'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner_view.xml',
    ],
    'Installable': False
}