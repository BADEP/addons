# -*- coding: utf-8 -*-

{
    'name': 'Delivery costs on products',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
    Add delivery costs directly on product price.
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['sale_stock', 'purchase'],
    'data': ['views.xml','security/ir.model.access.csv'],
    'installable': False,
}
