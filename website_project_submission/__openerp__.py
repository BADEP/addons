{
    'name': 'Website Project Submission',
    'category': 'Website',
    'version': '1.0',
    'summary': 'Offer Descriptions And Application Forms',
    'description': """
OpenERP Contact Form
====================

        """,
    'author': 'BADEP',
    'depends': ['project_submission', 'website_mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/website_project_submission_security.xml',
        'data/config_data.xml',
        'views/project_offer_views.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
