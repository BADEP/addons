# -*- coding: utf-8 -*-
{
    'name': "Atachements Optimization",

    'summary': """Automatically compress PDF and Image attachements to a reasonable size""",

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_setup'],
    #'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    # 'external_dependencies': {
    #     'python': [
    #         'pyfcm',
    #     ],
    # },
    # always loaded
    'data': [
        'data/ir_cron.xml',
        'views/res_config_settings_views.xml'
    ],
    'Installable': False
}