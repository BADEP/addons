# -*- coding: utf-8 -*-
{
    'name': "Sale Partner Delivery Info",

    'summary': """
        """,

    'description': """
        Adds delivery information in contact form to be used automatically in sale orders.
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '10.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock'],
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner_view.xml',
    ],
}