from odoo import http
from odoo.http import request
from datetime import datetime, date, timedelta

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

        # Obtener la hora actual
        current_time = datetime.now()

        # Ajustar la hora restando 6 horas
        adjusted_time = current_time - timedelta(hours=6)
        # Definir el inicio del día actual desde medianoche (00:00:00)
        today_start = datetime.combine(date.today(), datetime.min.time())

        # Definir el final del día actual extendido 6 horas (hasta las 06:00 AM del día siguiente)
        extended_end_of_today = today_start + timedelta(days=1, hours=6)


        # Buscar registros de asistencia de hoy para el empleado
        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', today_start),   # Desde el inicio del día actual (00:00:00 de hoy)
            ('check_in', '<=', extended_end_of_today)  # Hasta las 06:00:00 del día siguiente
        ], limit=1)

        if attendance:
            if attendance.hora_de_comida:
                attendance.sudo().write({'regreso_de_comida': current_time})
                message = 'Su hora de regreso ha sido registrada'
            else:
                attendance.sudo().write({'hora_de_comida': current_time})
                message = 'Su hora de comida ha sido registrada'
        else:
            return request.render('lunch_time.attendance_page', {
                'error': 'No se encontró un registro de asistencia para hoy.'
            })

        return request.render('lunch_time.confirmation_page', {
            'employee_name': employee.name,
            'current_time': adjusted_time.strftime('%Y-%m-%d %H:%M:%S'),
            'message': message
        })


