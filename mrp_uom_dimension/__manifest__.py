# -*- coding: utf-8 -*-

{
    'name': 'Product dimensions',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
    This module allow to have multidimensional UoMs.
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['stock_uom_dimension', 'mrp'],
    'data': [
             'security/ir.model.access.csv',
             'views/mrp_view.xml'
             ],
    'installable': False,
    'auto_install': True,
    'price': 50,
    'currency': 'USD'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
