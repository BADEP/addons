# -*- coding: utf-8 -*-
{
    'name': "Origin as delivery note in invoice",

    'summary': """
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

    # any module necessary for this one to work correctly
    'depends': [
                'sale_stock',
               ],
    'data': [
             ],
    'installable': True,
    'auto_install': False
}
