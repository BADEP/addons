# -*- coding: utf-8 -*-
{
    'name': "POS Category color",

    'summary': """
        Display the table on the color that the current order has""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '10.0.1',

    # any module necessary for this one to work correctly
    'depends': ['pos_restaurant', 'web_widget_color'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_view.xml',
    ],
}