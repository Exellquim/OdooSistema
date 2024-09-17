# -*- coding: utf-8 -*-
{
    'name': 'Multi Invoice Reconciliation | Invoice Partial Payment Reconcile Reconciliation',
    'version': '17.0.0.0.0',
    'author': 'Preway IT Solutions',
    'category': 'Accounting',
    'summary': 'Allows you to reconcile partial/full payments with multiple invoices/bills | Invoice Payment Reconciliation',
    'sequence': 10,
    'description': """
This module allows you to partially or fully reconcile multiple invoices/bills during payment.
    """,
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv', 
        'views/account_payment_view.xml',  
    ],
    'price': 60.0,
    'currency': 'EUR', 
    'live_test_url': 'https://youtu.be/M9UioY72xko',  
    'license': 'LGPL-3',  # Odoo 17 requiere especificar la licencia
    'images': ['static/description/Banner.png'], 
}
