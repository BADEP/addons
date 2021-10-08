{
    'name': "Website Sale Operating Unit",

    'summary': """
        Choose proper warehouse when sale order is generated from website""",
    'author': "BADEP",
    'website': "https://badep.ma",
    'category': 'Sales Management',
    'version': '13.0.1.0.1',
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'depends': ['website_sale', 'operating_unit'],
    'data': [
             'views/res_config_settings_views.xml',
             ],
    'auto_install': True,
    'installable': True,
    'price': 30,
    'currency': 'EUR'
}