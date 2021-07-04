# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Maroc - Paie avec comptabilité',
    'category': 'Human Resources',
    'depends': ['l10n_ma_hr_payroll', 'hr_payroll_account', 'l10n_ma'],
    'description': """
Accounting Data for Belgian Payroll Rules.
==========================================
    """,

    'auto_install': True,
    'data':[
        'data/l10n_ma_hr_payroll_account_data.xml',
    ],
    'post_init_hook': '_set_accounts',
    'installable': False,
}
