# -*- coding: utf-8 -*-
{
    'name': "Odoo Push Notifications",

    'summary': """Add push notifications for incoming messages using FCM""",

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Discuss',
    'version': '14.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['mail_bot', 'web'],
    'images': ['static/src/img/banner.png'],
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
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml'
    ],
}
