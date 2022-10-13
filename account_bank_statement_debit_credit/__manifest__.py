# -*- coding: utf-8 -*-
{
    'name': "Account Bank Statement Debit Credit",

    'summary': """
        Add debit and credit columns to bank statements""",

    'description': """
        
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    'category': 'Invoicing &amp; Payments',
    'version': '14.0.1.0',

    'depends': ['account'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'data': [
        'views/account_bank_statement_line_views.xml',
    ],
    'installable': True,
    'price': 49.00,
    'currency': 'EUR',
}