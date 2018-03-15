# -*- coding: utf-8 -*-
{
    'name': "Odoo Facebook Leads",

    'summary': """
        Sync Facebook Leads with CRM""",

    'description': """
    EXPERIMENTAL: Although this module works, it is in early development stage and is bound to change a lot. Please check frequently for updates.
    #TODO:
    -Better checks in field types (only normal fields and Many2one fields are mappable right now)
    -Better Documentation
    -Use native facebookads python library for:
        -Generate long lived token automatically
        -Fetch forms automatically
        -Fetch fields automatically
        -(Maybe) generate token directly from Odoo
        -A lot of cool stuff
    -Map with any model (for example mass mailing contacts). this is actually quite easy to do but not the main purpose of this module.
    #HOWTO:
    -You nead to create an app in developers.facebook.com with Marketing API enabled
    -Grant access to the page (should be automatic if you are the admin of the page AND the app)
    -Generate long lived access token (#TODO, but you can look up google for it)
    -Get your Lead Form info (Form ID and field names): You can easily get those in the csv header of the file you download from facebook ads
    -Create in Odoo your Facebook forms with the correct info (form id, access token and mappings) in Sales / Configuration / Leads and Opportunities / Facebook forms
    """,

    'author': "BADEP",
    'website': "https://badep.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '10.0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/crm_view.xml',
    ],
}