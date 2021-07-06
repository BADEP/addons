# -*- coding: utf-8 -*-

{
    'name' : 'Sale UoM Dimension Measure',
    'version': '14.0',
    'category': 'Sale',
    'summary':  """Sale lines measures""",
    'author': 'BADEP',
    'description': """
        Sale lines meausres
    """,
    'depends': ['sale_uom_dimension', 'sale_stock_manual_launch', 'sale_order_maps'],
    'data': [
             'security/security.xml',
             'security/ir.model.access.csv',
             'wizards/launch_measures_wizard_view.xml',
             'views/views.xml',
             'views/product_views.xml',
    ],
    'installable' : True,
}
