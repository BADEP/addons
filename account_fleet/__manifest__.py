# -*- coding: utf-8 -*-
{
    'name': "Account Fleet",

    'summary': """
        Link Invoices with Fleet""",

    'description': """
        Add vehicles and drivers assignation on Invoices. These Statistics can also be accessed directly from the vehicle view.
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    'category': 'Invoicing &amp; Payments',
    'version': '13.0.2.0',

    'depends': ['account', 'fleet'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'data': [
        'views/account_view.xml',
        'views/fleet_view.xml',
    ],
    'installable': False,
    'price': 49.00,
    'currency': 'USD',
}