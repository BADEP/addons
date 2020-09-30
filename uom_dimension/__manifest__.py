{
    'name': "Dimensions in Product UoM",

    'summary': """
        Eeach Unit of Measure has its dimensions. This is a technical module, functional behavior can be found in corresponding modules (stock_uom_dimension, sale_uom_dimension, purchase_uom_dimension).""",
    'author': "BADEP",
    'website': "https://badep.ma",
    'category': 'Inventory',
    'version': '14.0.1.0.1',
    'depends': ['uom'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/uom_view.xml',
    ],
    'Installable': False,
    'price': 20,
    'currency': 'USD'
}