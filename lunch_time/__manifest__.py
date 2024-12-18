{
    'name': 'Lunch Time',
    'version': '17.0.1.0.0',  # Indica la versión del módulo (Odoo 18)
    'license': 'LGPL-3',
    'summary': 'Module for managing lunch times',
    'sequence': 10,
    'description': 'This module allows employees to manage their lunch times',
    'category': 'Human Resources',
    'website': 'https://www.example.com',
    'depends': [
        'base',               
        'hr_attendance',        
        'website'            
    ],
    'data': [
         'views/hr_attendance_views.xml',
         'views/hr_attendance.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_frontend': [
            # 'lunch_time/static/src/css/attendance.css',  
        ],
        
    },
    #'license': 'LGPL-3',
}


