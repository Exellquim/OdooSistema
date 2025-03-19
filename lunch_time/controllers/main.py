from odoo import http
from odoo.http import request
from datetime import datetime
import pytz

class LunchTime(http.Controller):

    @http.route('/lunch_time/page', type='http', auth='user', website=True)
    def lunch_time_page(self, **kw):
        return request.render('lunch_time.attendance_page', {})

    @http.route('/lunch_time/submit', type='http', auth='user', website=True, csrf=False)
    def lunch_time_submit(self, **post):
        barcode = post.get('barcode')
        if not barcode:
            return request.render('lunch_time.attendance_page', {
                'error': 'Por favor, ingrese un código de barras válido.'
            })
        
        employee = request.env['hr.employee'].sudo().search([('barcode', '=', barcode)], limit=1)
        if not employee:
            return request.render('lunch_time.attendance_page', {
                'error': 'Empleado no encontrado.'
            })

        # Obtener la zona horaria de México
        tz = pytz.timezone('America/Mexico_City')

        # Obtener la hora actual en la zona horaria de México
        current_time = datetime.now(tz)
        today_date = current_time.date()

        # Convertir la hora de comida y regreso a la zona horaria de México
        naive_current_time = current_time.replace(tzinfo=None)  # Convertir a naive antes de registrar

        # Buscar la asistencia del día solo por empleado y registro (ya calculado)
        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('registro', '=', today_date)
        ], limit=1)

        if not attendance:
            return request.render('lunch_time.attendance_page', {
                'error': 'No se encontró un registro de asistencia para hoy.'
            })

        # Registrar hora de comida si no ha sido registrada
        if not attendance.hora_de_comida:
            # Ya hemos convertido la hora a naive y la registramos
            attendance.sudo().write({'hora_de_comida': naive_current_time})
            message = 'Su hora de comida ha sido registrada.'
        
        # Registrar hora de regreso de comida si no ha sido registrada
        elif not attendance.regreso_de_comida:
            # Ya hemos convertido la hora a naive y la registramos
            attendance.sudo().write({'regreso_de_comida': naive_current_time})
            message = 'Su hora de regreso de comida ha sido registrada.'
        
        # Si ambos ya están registrados
        else:
            message = 'Ya registró su hora de comida y regreso.'

        return request.render('lunch_time.confirmation_page', {
            'employee_name': employee.name,
            'current_time': naive_current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'message': message
        })
