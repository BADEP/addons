# -*- coding: utf-8 -*-
{
    'name': "Sale Project Section",

    'summary': """
        Generate parent tasks for project sections
    """,

    'description': """
        This module will automatically generate parent tasks for sections in sale orders. each task will have the corresponding sale order lines within that section as subtasks.
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    'category': 'Hidden',
    'version': '14.0.2.0',

    'depends': ['sale_project'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'data': [
    ],
    'installable': True,
    'price': 49.00,
    'currency': 'EUR',
}