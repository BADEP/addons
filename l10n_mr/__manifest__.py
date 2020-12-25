{
    'name' : 'Plan comptable Mauritanie',
    'version' : '12.0.0.1',
    'author' : 'Africa Performances, BADEP',
    'category' : 'Localization/Account Charts',
    'description': 	"""
					Accounting chart PCM for Mauritania.
					- Account type from Annual Financial Statement
					- VAT Taxes and Fiscal Position (TO DO)
					""",
    'website': 'https://badep.ma/',
    'depends' : ['account', 'base_vat'],
    'demo' : [],
    'data' : [
        'data/account_data.xml',
        'data/l10n_mr_chart_data.xml',
        'data/account_tax_data.xml',
        'data/account_chart_template_data.xml',
    ],
    'installable': False,
}