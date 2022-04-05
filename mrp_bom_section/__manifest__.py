# -*- coding: utf-8 -*-
{
    'name': "MRP Bom sections",

    'summary': """
        Add sections in MRP boms for better visibility""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    'category': 'Manufacturing/Manufacturing',
    'version': '14.0.1.0',

    'depends': ['mrp'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'data': [
        'views/mrp_bom_views.xml'
    ],
    'installable' : True,
}