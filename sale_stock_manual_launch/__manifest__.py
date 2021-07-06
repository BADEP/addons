# -*- coding: utf-8 -*-

{
    'name' : 'Sale Stock Manual Lauch Procurement',
    'version': '14.0',
    'category': 'Sale',
    'author': 'BADEP',
    'description': """
    """,
    'depends': ['sale_stock'],
    'data': [
             'security/ir.model.access.csv',
             'wizards/launch_procurement_wizard_view.xml',
             'views/views.xml',
    ],
    'installable' : True,
}
