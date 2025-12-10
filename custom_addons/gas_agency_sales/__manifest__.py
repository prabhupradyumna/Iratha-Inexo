# in gas_agency_sales/__manifest__.py
{
    'name': 'Gas Agency Sales',
    'version': '1.0',
    'category': 'Sales/Specific Industries',
    'summary': 'Adds custom fields to sales orders for Gas Agency cylinder management.',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'stock',
    ],
    'data': [
        'views/sale_order_views.xml', # Just the view file
    ],
    'installable': True,
    'application': True,
}