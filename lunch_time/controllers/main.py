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

        # Obtener la fecha actual en la zona horaria del usuario
        tz = request.env.user.tz or 'UTC'
        user_tz = pytz.timezone(tz)
        current_time = datetime.now(user_tz)
        today_date = current_time.date()

        # Buscar la asistencia del día solo por empleado y registro (ya calculado)
        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('registro', '=', today_date)
        ], limit=1)

        if not attendance:
            return request.render('lunch_time.attendance_page', {
                'error': 'No se encontró un registro de asistencia para hoy.'
            })

        # Registrar hora de comida o regreso de comida
        if not attendance.hora_de_comida:
            attendance.sudo().write({'hora_de_comida': current_time.replace(tzinfo=None)})
            message = 'Su hora de comida ha sido registrada'
        elif not attendance.regreso_de_comida:
            attendance.sudo().write({'regreso_de_comida': current_time.replace(tzinfo=None)})
            message = 'Su hora de regreso ha sido registrada'
        else:
            message = 'Ya registró su hora de comida y regreso.'

        return request.render('lunch_time.confirmation_page', {
            'employee_name': employee.name,
            'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'message': message
        })
