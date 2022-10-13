{
    'name' : 'Sale Stock Manual Lauch Procurement',
    'summary': 'Manually specify quantity to send to procurement in sales',
    'description': 'Manually specify quantity to send to procurement in sales',
    'version': '16.0.1.1',
    'category': 'Sales',
    'author': 'BADEP',
    'website': "https://badep.ma",
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',

    'depends': ['sale_stock'],
    'data': [
             'security/ir.model.access.csv',
             'wizards/launch_procurement_wizard_view.xml',
             'views/views.xml',
    ],
    'installable': False,
    'price': 99.00,
    'currency': 'EUR',
}