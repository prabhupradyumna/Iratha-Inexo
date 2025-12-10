{
    'name': 'Gas Agency Ledger',  # <-- Renamed to be more accurate
    'version': '1.0',
    'category': 'Sales/Specific Industries',
    'summary': 'Adds a custom partner ledger for commercial gas agency sales.',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',  # <-- DEPENDENCY: This is the Sales app
        'account',  # <-- DEPENDENCY: This is the Invoicing app
    ],
    'data': [
        'views/gas_payment_views.xml',
        'views/res_partner_views.xml',
        'views/gas_ledger_views.xml',
        'views/gas_agency_menus.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        # We will add the main ledger view here
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
