{
    'name': 'Lunch Time',
    'version': '1.0',
    'summary': 'Module for managing lunch times',
    'description': 'This module allows employees to manage their lunch times',
    'category': 'Human Resources',
    'author': 'RADAXBS',
    'website': 'https://www.example.com',
    'depends': [
        'base',                # Dependencia principal de Odoo
        'hr_attendance',        # Módulo de asistencia de recursos humanos
        'website',              # Funcionalidad de sitio web
    ],
    'data': [
        'views/hr_attendance_views.xml',  # Verifica que las vistas sean compatibles
        'views/hr_attendance.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'lunch_time/static/src/css/attendance.css',  # Asegúrate de que la ruta del asset es correcta
        ],
    },
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',  # Especifica la licencia para Odoo 17
}




