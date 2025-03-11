from odoo import http
from odoo.http import request
from datetime import datetime
import pytz  # Importar pytz para el manejo de zonas horarias
from pytz import timezone, UTC

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

        # Definir la zona horaria de México
        tz = pytz.timezone('America/Mexico_City')

        # Obtener la hora actual en la zona horaria de México correctamente
        current_time_mx = datetime.now().astimezone(tz)

        # Convertir a naive datetime antes de guardar
        naive_current_time = current_time_mx.replace(tzinfo=None)

        # Definir el inicio y fin del día actual en la zona horaria de México
        start_of_day_mx = naive_current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day_mx = naive_current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Buscar registros de asistencia dentro del día en horario de México
        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', start_of_day_mx),
            ('check_in', '<=', end_of_day_mx)
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
            'current_time': current_time_mx.strftime('%Y-%m-%d %H:%M:%S'),
            'message': message
        })
