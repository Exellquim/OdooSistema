{
    'name': 'Custom Account Reports - Impuesto en Antigüedad de Saldos',
    'version': '1.0.0',
    'summary': 'Agrega la columna de impuesto total en el reporte de Antigüedad de Saldos',
    'description': """
        Este módulo extiende el reporte de Antigüedad de Saldos (Aged Receivable Report)
            para mostrar una columna adicional con el total de impuestos asociados
            a cada factura o partner, tanto en el reporte en pantalla como en el PDF.
    """,
    'author': 'RBS-HEPL',
    'license': 'LGPL-3',
    'depends': [
        'account_reports',
    ],
    'data': [
        'views/account_aged_receivable_report_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
