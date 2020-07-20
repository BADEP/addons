{
    'name': "UoM Dimensions in Sales",

    'summary': """
        Allows the use of UoM dimensions in sales.""",
    'author': "BADEP",
    'website': "https://badep.ma",
    'category': 'Sales Management',
    'version': '12.0.1.0.1',
    'images': ['static/scr/img/banner.png'],
    'license': 'AGPL-3',
    'depends': ['sale', 'uom_dimension', 'web_m2x_options'],
    'data': [
             'views/sale_views.xml',
             'security/ir.model.access.csv',
             ],
    'auto_install': True,
    'Installable': True,
    'price': 30,
    'currency': 'EUR'
}