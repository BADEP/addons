{
    'name': 'Variable quantity in production',
    'version': '14.0.3.0.0',
    'license': 'AGPL-3',
    'author': "OCA, BADEP",
    'website': 'https://badep.ma',
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_line_formula_view.xml',
        'views/mrp_bom_view.xml',
    ],
    'installable': True,
}
