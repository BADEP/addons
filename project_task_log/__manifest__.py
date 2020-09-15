# -*- coding: utf-8 -*-
{
    'name': "Project Task Log",

    'summary': """
        Log Project Task changes: Assignation and stage""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project',

    # any module necessary for this one to work correctly
    'depends': ['project', 'web_widget_time_delta'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/project_task_log_security.xml',
        'views/task_view.xml'
    ],
    'installable': True,
    'price': 19.00,
    'currency': 'USD',
}