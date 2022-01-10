# -*- coding: utf-8 -*-
{
    'name': "Purchase Project",

    'summary': """
        Link Purchases with Project""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    'category': 'Project',
    'version': '14.0.1.0',

    'depends': ['project_purchase_link'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'data': [
        'views/project_view.xml',
        'views/purchase_view.xml',
    ],
    'installable': True,
    'price': 49.00,
    'currency': 'EUR',
}