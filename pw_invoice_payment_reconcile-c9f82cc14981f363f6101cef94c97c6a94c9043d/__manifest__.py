# -*- coding: utf-8 -*-
{
    'name': 'Multi Invoice Reconciliation | Invoice Partial Payment Reconcile Reconciliation',
    'version': '1.0',
    'author': 'Preway IT Solutions',
    'category': 'Accounting',
    'summary': 'Allows you to reconcile partial/full payments with multiple invoices/bills | Invoice Payment Reconciliation',
    'description': """
This module allows you to partially or fully reconcile multiple invoices/bills during payment.
    """,
    'depends': ['account'],  # Verifica que el módulo 'account' sea compatible con Odoo 17
    'data': [
        'security/ir.model.access.csv',  # Asegúrate de que los permisos sean correctos para Odoo 17
        'views/account_payment_view.xml',  # Verifica que las vistas sean compatibles con Odoo 17
    ],
    'price': 60.0,
    'currency': 'EUR',
    'application': True,
    'installable': True,
    'auto_install': False,  # Si no deseas que se instale automáticamente
    'live_test_url': 'https://youtu.be/M9UioY72xko',  # Opcional, pero bueno incluirlo si el enlace es válido
    'license': 'LGPL-3',  # Odoo 17 requiere especificar la licencia
    'images': ['static/description/Banner.png'],  # Asegúrate de que la imagen esté en la ruta correcta
}
