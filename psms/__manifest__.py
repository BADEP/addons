# -*- coding: utf-8 -*-

{
    'name': 'Petrol Station Management System',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
    """,
    'author': 'BADEP, Pragmatic System',
    'website': 'http://www.badep.ma, http://pragmatic-system.ma',
    'depends': ['stock',
                'product',
                'sale_management',
                'purchase', 'mail',
                'base',
                'fleet',
                'hr',],
    'data': [
            'account_view.xml',
             'product_view.xml',
             'sale_view.xml',
             'fleet_view.xml',
             'hr_employee.xml',
             #'report/sale_report_view.xml',
             'report/account_invoice_report_view.xml',
             'security/ir.model.access.csv'],
    'installable': True,
    'application': True,
}
