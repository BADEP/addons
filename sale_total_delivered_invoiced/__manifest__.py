# -*- coding: utf-8 -*-
{
    'name': "Total Delivered & Invoiced in Sale Orders",

    'summary': """
        """,

    'description': """
        Adds total delivered and invoiced in sale orders
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_view.xml',
    ],
    'installable': False,
}