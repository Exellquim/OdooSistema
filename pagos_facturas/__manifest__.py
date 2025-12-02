{
    'name': 'Facturas con Pagos',
    'version': '1.0',
    'depends': ['account'],
    'author': 'RBS-HEPL',
    'category': 'Accounting',
    'data': [
        'security/ir.model.access.csv',
        'views/facturas_pagos_menu.xml',
        'views/facturas_pagos_excel_wizard_view.xml',
    ],
    'installable': True,
}
