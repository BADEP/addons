# -*- coding: utf-8 -*-
{
    'name': "Dimensions in Product UoM",

    'summary': """
        Eeach Unit of Measure has its dimensions. This is a technical module, functional behavior can be found in corresponding modules (stock_uom_dimension, sale_uom_dimension, purchase_uom_dimension).""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '11.0.1',

    # any module necessary for this one to work correctly
    'depends': ['uom'],
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/uom_view.xml',
    ],
    'installable': False,
}