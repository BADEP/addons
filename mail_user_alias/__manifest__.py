# -*- coding: utf-8 -*-
{
    'name': "mail_user_alias",

    'summary': """Restore mail alias behavior for Users in v12 """,

    'description': """
        This module intends to restore mail_alias behaviors for Users in such a way that an incoming email with the proper alias will be redirected in the user Inbox.
        Also adds a button for easy alias creation.
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    'category': 'Discuss',
    'version': '12.0.0.1',

    'depends': ['mail'],

    'data': [
        'views/res_users_view.xml'
    ],
}