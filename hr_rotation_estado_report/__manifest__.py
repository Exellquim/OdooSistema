{
  'name': 'Reporte de Rotación por Estado',
  'summary': 'Tabla y gráfica de rotación por estado del empleado',
  'version': '17.0.1.0',
  'category': 'Human Resources',
  'license': 'LGPL-3',
  'author': 'Tu Organización',
  'depends': ['hr', 'web'],
  'data': [
    #'security/ir.model.access.csv',
    'views/employee_rotation_views.xml',
  ],
  'installable': True,
  'application': False,
}

