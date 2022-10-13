{
    'name': 'Sale Maps',
    'summary': """Map view in Sales""",
    'description': """
Sale Maps
========

Show your Sale orders  on map view in regards to delivery address
""",
    'author': "BADEP, Vauxoo",
    'website': "https://badep.ma",

    'version': '16.0.1.0.0',
    'author': 'BADEP',
    'website': "https://badep.ma",
    'license': 'AGPL-3',
    'maintainer': 'Yopi Angi <yopiangi@gmail.com>, Khalid Hazam <k.hazam@badep.ma>',
    'category': 'Sales',
    'images': ['static/src/img/banner.png'],

    'depends': [
        'sale',
        'contacts_maps'
    ],
    'data': [
        'views/sale_views.xml'
    ],
    'installable': False,
    'demo': [],
    'uninstall_hook': 'uninstall_hook',
    'price': 29.00,
    'currency': 'EUR',
}
