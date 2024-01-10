# -*- coding: utf-8 -*-
{
    'name': "Asistencia",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Antonia Maya Pichardo",
    'website': "amaya@radax.mx",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','hr','hr_attendance'],

    'data': [
        'views/asistencia.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
