{
    'name': "Ledger Smart Menu",

    'summary': 'Partner ledger quick view with running balance',
    'description': """
    """,

    'author': "Irshad K T",
    'website': "www.linkedin.com/in/irshadkt",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.6',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'templates/partner_ledger_template.xml',
        'templates/partner_leger_action.xml',
        'views/partner_ledger.xml',
        'views/partner_ledger_views.xml',
        'wizard/partner_ledger_wizard.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
    'images':[
        'static/description/banner.gif',
    ],
    'instalable':True,
    'application':True,
    'aut_install': False,
}

