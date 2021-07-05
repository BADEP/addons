# -*- coding: utf-8 -*-
{
    'name': 'Fleet Maps',
    'version': '14.0.1.0.2',
    'author': 'Yopi Angi, BADEP',
    'license': 'AGPL-3',
    'maintainer': 'Yopi Angi <yopiangi@gmail.com>, Khalid Hazam <k.hazam@badep.ma>',
    'support': 'yopiangi@gmail.com',
    'category': 'Fleet',
    'description': """
Fleet Maps
========

Show your leads and pipelines on map
""",
    'depends': [
        'fleet',
        'web_google_maps'
    ],
    'data': [
        'views/fleet_vehicle.xml'
    ],
    'demo': [],
    'installable': False,
    'uninstall_hook': 'uninstall_hook',
}
