# Copyright 2016-2019 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Variable quantity in production',
    'version': '12.0.3.0.0',
    'license': 'AGPL-3',
    'author': "OCA, BADEP, Pragmatic System",
    'website': 'https://www.tecnativa.com',
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_line_formula_view.xml',
        'views/mrp_bom_view.xml',
    ],
    'installable': True,
}
