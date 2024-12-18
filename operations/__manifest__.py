# -*- coding: utf-8 -*-
{
    'name': "Operations MO",

    'summary': """ """,
   
    'description': """
Entregas
    """,

    'author': "",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.0.0',  # Indica la versión del módulo (Odoo 17)
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','sale'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'views/operations_stock_move.xml',
        'views/perations_stock_move_unit.xml',
        'views/sale.order.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}

