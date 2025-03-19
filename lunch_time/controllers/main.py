from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
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

        # Sumar 6 horas a la hora actual
        current_time_plus_6 = current_time + timedelta(hours=6)

        # Convertir la hora a naive (sin zona horaria) para registrarla correctamente
        naive_current_time_plus_6 = current_time_plus_6.replace(tzinfo=None)

        # Buscar la asistencia del día solo por empleado y registro (ya calculado)
        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('registro', '=', today_date)
        ], limit=1)

        if not attendance:
            return request.render('lunch_time.attendance_page', {
                'error': 'No se encontró un registro de asistencia para hoy.'
            })

        # Si la hora de comida no ha sido registrada, la registramos
        if not attendance.hora_de_comida:
            # Registrar hora de comida
            attendance.sudo().write({'hora_de_comida': naive_current_time_plus_6})
            message = 'Su hora de comida ha sido registrada.'
        
        # Si la hora de regreso de comida no ha sido registrada, la registramos
        elif not attendance.regreso_de_comida:
            # Validamos que ya exista la hora de comida registrada
            if attendance.hora_de_comida:
                attendance.sudo().write({'regreso_de_comida': naive_current_time_plus_6})
                message = 'Su hora de regreso de comida ha sido registrada.'
            else:
                message = 'Debe registrar primero la hora de comida.'

        # Si ambos ya están registrados
        else:
            message = 'Ya registró su hora de comida y regreso.'

        return request.render('lunch_time.confirmation_page', {
            'employee_name': employee.name,
            'current_time': naive_current_time_plus_6.strftime('%Y-%m-%d %H:%M:%S'),
            'message': message
        })

