{
    'name': 'Petrol Station Management System',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
    """,
    'author': 'BADEP, Pragmatic System',
    'website': 'http://www.badep.ma, http://pragmatic-system.ma',
    'depends': [
        'point_of_sale',
        'sale_management'
    ],
    'data': [
        'views/product_view.xml',
        'views/sale_view.xml',
         'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'price': 300.00,
    'currency': 'EUR',
}
