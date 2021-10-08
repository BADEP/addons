# -*- coding: utf-8 -*-
{
    'name': 'Stock Picking Maps',
    'version': '13.0.1.0.0',
    'author': 'Yopi Angi, BADEP',
    'license': 'AGPL-3',
    'maintainer': 'Yopi Angi <yopiangi@gmail.com>, Khalid Hazam <k.hazam@badep.ma>',
    'support': 'yopiangi@gmail.com',
    'category': 'Sales',
    'description': """
Stock Picking Maps
========

Show your Stock pickings  on map view in regards to delivery address
""",
    'depends': [
        'stock',
        'contacts_maps'
    ],
    'data': [
        'views/picking_views.xml'
    ],
    'demo': [],
    'installable': True,
    'uninstall_hook': 'uninstall_hook',
}
