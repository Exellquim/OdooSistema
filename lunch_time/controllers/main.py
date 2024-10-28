from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import pytz  # Importar pytz para el manejo de zonas horarias

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

        # Obtener la hora actual en UTC
        current_time_utc = datetime.now(pytz.utc)

        # Convertir a la zona horaria del usuario
        tz = request.env.user.tz  # Obtener la zona horaria del usuario
        if tz:
            user_tz = pytz.timezone(tz)
            current_time = current_time_utc.astimezone(user_tz)
        else:
            current_time = current_time_utc  # Si no hay zona horaria, usar UTC

        # Convertir a naive datetime antes de guardar
        naive_current_time = current_time.replace(tzinfo=None)

        # Definir el inicio y fin del día actual
        start_of_extended_day = naive_current_time.replace(hour=0, minute=0, second=0) - timedelta(hours=6)
        end_of_extended_day = naive_current_time.replace(hour=0, minute=0, second=0) + timedelta(days=1, hours=6)

        # Buscar registros de asistencia
        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', start_of_extended_day),
            ('check_in', '<=', end_of_extended_day)
        ], limit=1)

        if attendance:
            if attendance.hora_de_comida:
                attendance.sudo().write({'regreso_de_comida': naive_current_time})
                message = 'Su hora de regreso ha sido registrada'
            else:
                attendance.sudo().write({'hora_de_comida': naive_current_time})
                message = 'Su hora de comida ha sido registrada'
        else:
            return request.render('lunch_time.attendance_page', {
                'error': 'No se encontró un registro de asistencia para hoy.'
            })

        return request.render('lunch_time.confirmation_page', {
            'employee_name': employee.name,
            'current_time': naive_current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'message': message
        })
