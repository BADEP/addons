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
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
    ],
}