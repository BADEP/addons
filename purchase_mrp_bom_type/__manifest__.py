{
    'name': 'Purchase MRP Separate BOM Type',
    'author': 'BADEP',
    'version': '13.0.1',
    'category': 'Hidden',
    'description': """
Allow to define a bom type for purchases different than that of sales
    """,
    'depends': ['purchase_mrp'],
    'data': [
        'views/bom_views.xml'
    ],
    'installable': False,
    'price': 9.00,
    'currency': 'EUR',
}
