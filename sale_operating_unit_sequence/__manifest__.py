# -*- coding: utf-8 -*-
{
    'name': "Sale operating Unit Sequence",

    'summary': """
        Add OU specific sequence for sale orders""",

    'author': "BADEP",
    'website': "https://badep.ma",

    'category': 'Sales',
    'version': '12.0.1.0',

    'depends': ['sale_operating_unit'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'data': [
        'views/sequence_view.xml',
    ],
    'installable': True,
    'price': 49.00,
    'currency': 'eur',
}