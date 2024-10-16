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

        # Ajustar la hora restando 6 horas para mostrarla correctamente
        adjusted_time = current_time - timedelta(hours=6)

        # Definir el inicio del día actual extendido (06:00 PM del día anterior)
        start_of_extended_day = datetime.combine(date.today(), datetime.min.time()) - timedelta(hours=6)

        # Definir el final del día actual extendido (06:00 AM del día siguiente)
        end_of_extended_day = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1, hours=6)

        # Buscar registros de asistencia para el empleado, desde 6 horas antes hasta 6 horas después
        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', start_of_extended_day),  # Desde 6 horas antes de la medianoche
            ('check_in', '<=', end_of_extended_day)  # Hasta 6 horas después de la medianoche del siguiente día
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
