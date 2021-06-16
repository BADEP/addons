{
    'name': "UoM Dimensions in Sales",

    'summary': """
        Allows the use of UoM dimensions in sales.""",
    'author': "BADEP",
    'website': "https://badep.ma",
    'category': 'Sales Management',
    'version': '12.0.1.0.1',
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'depends': ['website_sale', 'sale_uom_dimension'],
    'data': [
             'views/sale_views.xml',
             ],
    'auto_install': True,
    'installable': True,
    'price': 30,
    'currency': 'EUR'
}