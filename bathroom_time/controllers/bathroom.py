
from odoo import http, fields
from odoo.http import request


class BathroomTime(http.Controller):

    @http.route('/bathroom_time/page', type='http', auth='user', website=True)
    def bathroom_page(self, **kw):
        return request.render('bathroom_time.bathroom_page')

    @http.route('/bathroom_time/submit', type='http', auth='user', website=True, methods=['POST'])
    def bathroom_submit(self, **post):
        barcode = post.get('barcode')
        employee = request.env['hr.employee'].sudo().search(
            [('barcode', '=', barcode)], limit=1
        )

        if not employee:
            return request.render(
                'bathroom_time.bathroom_page',
                {'error': 'Empleado no encontrado'}
            )

        now = fields.Datetime.now()

        att = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '<=', now),
            ('check_out', '=', False)
        ], limit=1)

        if not att:
            return request.render(
                'bathroom_time.bathroom_page',
                {'error': 'No hay asistencia activa'}
            )

        Log = request.env['bathroom.log'].sudo()
        open_log = Log.search([
            ('attendance_id', '=', att.id),
            ('end_time', '=', False)
        ], limit=1)

        if open_log:
            open_log.end_time = now
            msg = "Regreso del baño registrado"
        else:
            Log.create({
                'employee_id': employee.id,
                'attendance_id': att.id,
                'start_time': now
            })
            msg = "Salida al baño registrada"

        return request.render(
            'bathroom_time.bathroom_confirm',
            {'employee_name': employee.name, 'message': msg}
        )
