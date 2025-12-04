
from odoo import models, fields, api

class BathroomLog(models.Model):
    _name='bathroom.log'
    _description='Registro de baño'
    _order='start_time asc'

    employee_id=fields.Many2one('hr.employee',string="Empleado", required=True)
    attendance_id=fields.Many2one('hr.attendance',required=True)
    start_time=fields.Datetime(string="Fecha y hora de salida")
    end_time=fields.Datetime( string="Fecha y hora de regreso")
    duration_minutes=fields.Float(compute='_compute_dur', string="Tiempo" , store=True)

    @api.depends('start_time','end_time')
    def _compute_dur(self):
        for r in self:
            if r.start_time and r.end_time:
                r.duration_minutes=(r.end_time-r.start_time).total_seconds()/60
            else:
                r.duration_minutes=0

class HrAttendance(models.Model):
    _inherit='hr.attendance'
    bathroom_log_ids=fields.One2many('bathroom.log','attendance_id')
    bathroom_total_minutes=fields.Float(compute='_compute_total', store=True)

    @api.depends('bathroom_log_ids.duration_minutes')
    def _compute_total(self):
        for r in self:
            r.bathroom_total_minutes=sum(r.bathroom_log_ids.mapped('duration_minutes'))

    def action_view_bathroom(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registros de sanitarios',
            'res_model': 'bathroom.log',
            'view_mode': 'list,form',
            'domain': [('attendance_id', '=', self.id)],
            'target': 'new', 
            'context': {
                'default_attendance_id': self.id,
                'default_employee_id': self.employee_id.id,
            },
        }


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    
    number_of_days_display = fields.Float(
        string='Duration (days)',
        compute='_compute_number_of_days_display',
        inverse='_inverse_number_of_days_display',
        store=True,
        readonly=False,
    )

    @api.depends('number_of_days')
    def _compute_number_of_days_display(self):
        """Sigue funcionando como hasta ahora: toma el valor calculado."""
        for allocation in self:
            allocation.number_of_days_display = allocation.number_of_days

    def _inverse_number_of_days_display(self):
        """
        Se ejecuta cuando el usuario cambia manualmente number_of_days_display
        y guarda el registro. Aquí decides cómo impactar el valor 'real'.
        """
        for allocation in self:
            # Si la unidad es en días, el display se vuelve la fuente de la verdad
            if allocation.type_request_unit != 'hour':
                allocation.number_of_days = allocation.number_of_days_display
            else:
                # Si usas horas, lo puedes traducir a horas basado en el horario del empleado
                if allocation.employee_id and allocation.date_from:
                    hours_per_day = allocation.employee_id._get_hours_per_day(allocation.date_from)
                    allocation.number_of_hours_display = allocation.number_of_days_display * hours_per_day
