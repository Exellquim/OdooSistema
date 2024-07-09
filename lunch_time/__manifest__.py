# lunch_time/__manifest__.py

{
    'name': 'Lunch Time',
    'version': '1.0',
    'summary': 'Module for managing lunch times',
    'description': 'This module allows employees to manage their lunch times',
    'category': 'Human Resources',
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'depends': ['base', 'hr_attendance', 'website'],
    'data': [
        'views/hr_attendance_views.xml',
        #'views/confirmation_page.xml',
        # cualquier otro archivo XML necesario
    ],
    'assets': {
        'web.assets_frontend': [
            'lunch_time/static/src/css/attendance.css',
        ],
    },
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}



