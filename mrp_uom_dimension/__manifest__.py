# -*- coding: utf-8 -*-

{
    'name': 'Product dimensions',
    'version': '14.0',
    'category': 'Sales Management',
    'description': """
    This module allow to have multidimensional UoMs.
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['stock_uom_dimension', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_views.xml',
        'views/mrp_uom_dimension_templates.xml',
        'views/mrp_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'price': 50,
    'currency': 'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
