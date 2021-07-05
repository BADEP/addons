# -*- coding: utf-8 -*-

{
    'name': 'Product dimensions in stock',
    'version': '1.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'description': """
    This module allow to have multidimensional UoMs.
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['uom_dimension', 'stock'],
    'data': [
             'report/stock_picking_report_view.xml',
             'views/stock_view.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
    'auto_install': True,
    'price': 100,
    'currency': 'EUR'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
