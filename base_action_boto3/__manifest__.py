# -*- coding: utf-8 -*-
{
    'name': "boto3 in server actions",

    'summary': """Allow the use of boto3 lib in server actions
        """,

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '13.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base'
    ],
    'external_dependencies': {
        'python': [
            'boto3',
        ],
    },
    'installable': True,
    'auto_install': True,
}
