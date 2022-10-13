# -*- coding: utf-8 -*-

{
    'name': 'Product dimensions in stock_barcode Entreprise module',
    'version': '16.0',
    'category': 'Inventory',
    'license': 'AGPL-3',
    'description': """
    This module allow to have multidimensional UoMs in stock_barcode module.
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['stock_barcode', 'stock_uom_dimension'],
    'data': [
             'views/stock_move_line_views.xml',
             ],
    'installable': False,
    'auto_install': True,
    'price': 50,
    'currency': 'EUR'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
