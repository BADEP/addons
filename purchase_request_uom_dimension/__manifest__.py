{
    'name': "UoM Dimensions in purchases",

    'summary': """
        Allows the use of UoM dimensions in purchases.""",
    'author': "BADEP",
    'website': "https://badep.ma",
    'category': 'purchases Management',
    'version': '14.0.1.0.1',
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',
    'depends': ['purchase_request', 'uom_dimension'],
    'data': [
             'views/purchase_views.xml',
             'report/purchase_report_templates.xml',
             'security/ir.model.access.csv',
             ],
    'auto_install': False,
    'installable': False,
    'price': 30,
    'currency': 'EUR'
}