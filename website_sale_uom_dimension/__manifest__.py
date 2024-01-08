{
    'name': "UoM Dimensions in Website",

    'summary': """
        Allows the use of UoM dimensions in e-commerce.""",
    'author': "BADEP",
    'website': "https://badep.ma",
    'category': 'Sales Management',
    'version': '14.0.1.0.1',
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'depends': ['website_sale', 'sale_uom_dimension'],
    'data': [
             'views/sale_views.xml',
             'security/ir.model.access.csv'
             ],
    'auto_install': True,
    'installable': True,
}
