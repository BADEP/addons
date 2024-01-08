# -*- coding: utf-8 -*-

{
    'name': 'Product dimensions in stock',
    'version': '14.0',
    'category': 'Inventory',
    'license': 'AGPL-3',
    'description': """
    This module allow to have multidimensional UoMs.
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['uom_dimension', 'stock'],
    'data': [
             'report/stock_picking_report_view.xml',
             'views/product_views.xml',
             'views/stock_move_line_views.xml',
             'views/stock_move_views.xml',
             'views/stock_picking_views.xml',
             'views/stock_quant_views.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
    'auto_install': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
