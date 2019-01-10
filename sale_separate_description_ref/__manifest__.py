# -*- coding: utf-8 -*-
{
    'name': "Sale separated description and product code",

    'summary': """
        """,

    'description': """
    Removes product reference from sale order line descriptions and add a separate column for product code in sale report
    """,

    'author': "BADEP, Unique Système",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '10.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale',
               ],
    'data': [
        'views/report_saleorder.xml',
             ],
    'installable': True,
    'auto_install': False
}
