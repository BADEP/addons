# -*- coding: utf-8 -*-

{
    'name': "SMTP Per User",
    'version': '0.2',
    'summary': 'Send letters from Odoo using your own mail',
    'category': 'Mail',
    'description': """Can configure different mail servers per user""",
    'author': 'OERP',
    'license': 'AGPL-3',
    'website': "www.oerp.eu",
    "depends" : ['mail','base'],
    'data': [
        'smtp_per_user_view.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
}
