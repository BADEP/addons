# -*- coding: utf-8 -*-

{
    'name': 'Petrol Station Management System',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
    """,
    'author': 'BADEP',
    'website': 'http://www.badep.ma',
    'depends': ['stock', 'product', 'sale', 'purchase', 'mail', 'base', 'fleet', 'sale_taxed_total', 'hr'],
    'data': ['account_view.xml', 'product_view.xml', 'sale_view.xml', 'fleet_view.xml', 'report/sale_report_view.xml', 'report/account_invoice_report_view.xml', 'security/ir.model.access.csv'],
    'installable': True,
    'application': True,
}
