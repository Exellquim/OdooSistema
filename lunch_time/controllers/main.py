
from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta, time
import pytz


class LunchTime(http.Controller):

    @http.route('/lunch_time/page', type='http', auth='user', website=True)
    def lunch_time_page(self, **kw):
        return request.render('lunch_time.attendance_page', {})

    @http.route('/lunch_time/submit', type='http', auth='user',
                website=True, methods=['POST'])
    def lunch_time_submit(self, **post):
        barcode = post.get('barcode')

        if not barcode:
            return request.render('lunch_time.attendance_page', {
                'error': 'Por favor, ingrese un código de barras válido.'
            })

        employee = request.env['hr.employee'].sudo().search([
            ('barcode', '=', barcode)
        ], limit=1)

        if not employee:
            return request.render('lunch_time.attendance_page', {
                'error': 'Empleado no encontrado.'
            })

        tz = pytz.timezone('America/Mexico_City')
        now = fields.Datetime.now()
        current_time = pytz.UTC.localize(now).astimezone(tz)
        today_date = current_time.date()

        start = tz.localize(
            datetime.combine(today_date, time.min)
        ).astimezone(pytz.UTC).replace(tzinfo=None)

        end = tz.localize(
            datetime.combine(today_date + timedelta(days=1), time.min)
        ).astimezone(pytz.UTC).replace(tzinfo=None)

        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', start),
            ('check_in', '<', end)
        ], limit=1)

        if not attendance:
            return request.render('lunch_time.attendance_page', {
                'error': 'No se encontró un registro de asistencia para hoy.'
            })

        if not attendance.hora_de_comida:
            attendance.write({'hora_de_comida': now})
            message = 'Su hora de comida ha sido registrada.'

        elif not attendance.regreso_de_comida:
            attendance.write({'regreso_de_comida': now})
            message = 'Su hora de regreso de comida ha sido registrada.'

        else:
            message = 'Ya registró su hora de comida y regreso.'

        return request.render('lunch_time.confirmation_page', {
            'employee_name': employee.name,
            'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'message': message
        })
