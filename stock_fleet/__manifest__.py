# -*- coding: utf-8 -*-
{
    'name': "Stock Fleet",

    'summary': """
        Link Stock with Fleet""",

    'description': """
        Add vehicles and drivers assignation on Picking Orders and waves. These Statistics can also be accessed directly from the vehicle view.
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'fleet'],
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_view.xml',
        'views/fleet_view.xml',
    ],
}