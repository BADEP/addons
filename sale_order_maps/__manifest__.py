# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Maps',
    'version': '14.0.1.0.0',
    'author': 'Yopi Angi, BADEP',
    'license': 'AGPL-3',
    'maintainer': 'Yopi Angi <yopiangi@gmail.com>, Khalid Hazam <k.hazam@badep.ma>',
    'support': 'yopiangi@gmail.com',
    'category': 'Sales',
    'description': """
Sale Order Maps
========

Show your Sale orders  on map view in regards to delivery address
""",
    'depends': [
        'sale',
        'contacts_maps'
    ],
    'data': [
        'views/sale_views.xml'
    ],
    'demo': [],
    'installable': False,
    'uninstall_hook': 'uninstall_hook',
}
