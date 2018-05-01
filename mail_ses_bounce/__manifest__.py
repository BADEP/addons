# -*- coding: utf-8 -*-
{
    'name': "Mail SES Bounce",

    'summary': """Compatibilty module between Amazon SES Bounce and Odoo bounce logique
        """,

    'description': """
    EXPERIMENTAL: Although this module works, it is in early development stage and is bound to change a lot. Please check frequently for updates.
    #TODO:
    -Better checks
    -Better Documentation
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '10.0.1',
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['mail_tracking'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
}