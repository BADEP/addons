# -*- coding: utf-8 -*-
{
    'name': "Partner Shareholders",

    'summary': """Add shareholders info in partners and companies
        """,

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '14.0.1',

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
