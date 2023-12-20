# -*- coding: utf-8 -*-
{
    'name': "MRP Production Batch",

    'summary': """
        Batch Processing of MRP orders and workorders""",

    'description': """
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    'category': 'Manufacturing/Manufacturing',
    'version': '16.0.2.0',

    'depends': ['mrp_routing'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'data': [
        'data/mrp_production_batch_data.xml',
        'report/mrp_production_batch_templates.xml',
        'views/mrp_production_batch_views.xml',
        'views/mrp_workorder_batch_views.xml',
        'views/mrp_workcenter_views.xml',
        'views/product_attribute_views.xml',
        'security/ir.model.access.csv',
        'security/mrp_security.xml'
    ],
    'installable': True,
}