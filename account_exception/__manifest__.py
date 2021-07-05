# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# Copyright 2020 BADEP
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Exception',
    'summary': 'Custom exceptions on Invoices',
    'version': '14.0.1.1.1',
    'category': 'Generic Modules/Sale',
    'author': "Akretion, "
              "Sodexis, "
              "Camptocamp, "
              "BADEP, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': ['account', 'base_exception'],
    'license': 'AGPL-3',
    'data': [
        'data/account_exception_data.xml',
        'wizard/account_exception_confirm_view.xml',
        'views/invoice_view.xml',
    ],
    'installable': False
}
