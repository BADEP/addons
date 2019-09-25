# -*- coding: utf-8 -*-
{
    'name': "Project Task archive documents",

    'summary': """
        Automatically (de)archivate related task attachments""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project',

    # any module necessary for this one to work correctly
    'depends': ['project'],
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
}