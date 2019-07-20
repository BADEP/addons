# -*- coding: utf-8 -*-
{
    'name': "Purchase Fleet",

    'summary': """
        Link Purchases with Fleet""",

    'description': """
        Add vehicles and drivers assignation on RfQs and Sale Orders. These Statistics can also be accessed directly from the vehicle view.
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'stock_fleet'],
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_view.xml',
        'views/fleet_view.xml',
    ],
}