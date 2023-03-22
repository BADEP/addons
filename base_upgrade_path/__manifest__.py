# -*- coding: utf-8 -*-
{
    'name': "Check upgrade path",

    'summary': """Allow to check if module is upgradable in target version
        """,

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base'
    ],
    'data': [
        'data/ir_cron.xml',
        'views/ir_module_module_views.xml',
        'security/ir.model.access.csv'
     ],
    'installable': True,
}
