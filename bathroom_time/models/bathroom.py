
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
        readonly=False,
        # store=True  # opcional, por defecto los Float se guardan
    )
