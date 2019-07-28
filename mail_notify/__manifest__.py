# -*- coding: utf-8 -*-
{
    'name': "Mail Push Notifications",

    'summary': """Add push notifications for incoming messages""",

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Discuss',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'web'],
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'pyfcm',
        ],
    },
    # always loaded
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'security/mail_notify_security.xml',
        'views/assets.xml',
        'views/res_config_settings_views.xml'
    ],
}