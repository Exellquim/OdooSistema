
{
    'name': 'Bathroom Time',
    'version': '1.0',
    'summary': 'Registro de tiempos de baño desde kiosko',
    'depends': ['hr_attendance', 'hr_holidays', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/bathroom_views.xml',
        'views/bathroom_kiosk.xml',
    ],
    'installable': True,
}
