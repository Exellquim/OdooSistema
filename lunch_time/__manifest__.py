{
    'name': 'Lunch Time',
    'version': '17.0.0.0.0',
    'summary': 'Module for managing lunch times',
    'description': 'This module allows employees to manage their lunch times',
    'sequence': 10,
    'category': 'Human Resources',
    'author': 'RADAXBS',
    'website': 'https://www.example.com',
    'depends': [
        'base',               
        'hr_attendance',        
        'website',              
    ],
    'data': [
        'views/hr_attendance_views.xml',
        'views/hr_attendance.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'lunch_time/static/src/css/attendance.css',  
        ],
    },
    'license': 'LGPL-3',  # Especifica la licencia para Odoo 17
    
}


