{
    'name': "UoM Dimensions in Invoices",

    'summary': """
        Allows the use of UoM dimensions in invoices.""",
    'author': "BADEP",
    'website': "https://badep.ma",
    'category': 'Invoicing Management',
    'version': '12.0.1.0.1',
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',
    'depends': ['account', 'uom_dimension', 'web_m2x_options'],
    'data': [
             'views/invoice_views.xml',
             'security/ir.model.access.csv',
             ],
    'auto_install': True,
    'Installable': False,
    'price': 30,
    'currency': 'EUR'
}