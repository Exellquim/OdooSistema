# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

ESTADO_FIELD = "x_studio_estado_del_empleado"  


def _month_bounds(any_day: date):
    """Return (month_start, next_month_start, month_end) for any_day."""
    mstart = any_day.replace(day=1)
    nstart = mstart + relativedelta(months=1)
    mend = nstart - relativedelta(days=1)
    return mstart, nstart, mend


class EmployeeRotationReportWizard(models.TransientModel):
    _name = "employee.rotation.report.wizard"
    _description = "Asistente: Reporte de Rotacion por Estado"

    target_month = fields.Date(
        string="Mes a consultar",
        required=True,
        default=lambda self: fields.Date.context_today(self),
        help="Seleccione una fecha dentro del mes objetivo (p. ej. 2025-08-15 -> Agosto 2025).",
    )

    line_ids = fields.One2many(
        "employee.rotation.report.line", "wizard_id", string="Resultados"
    )

    def _employees_present_on(self, day: date):
        """
        Empleados presentes al cierre de 'day'.
        Criterio:
          - create_date < primer_dia_mes_siguiente(day)
          - departure_date vacio o > day
        Incluye activos y archivados (active_test=False).
        """
        self = self.with_context(active_test=False)
        _, next_month_start, _ = _month_bounds(day)
        domain = [
            ("create_date", "<", datetime.combine(next_month_start, datetime.min.time())),
            "|",
            ("departure_date", "=", False),
            ("departure_date", ">", day),
        ]
        return self.env["hr.employee"].sudo().search_read(domain, [ESTADO_FIELD], limit=0)

    def _employees_archived_in_month(self, mstart: date, nstart: date):
        """Empleados con departure_date en [mstart, nstart)."""
        self = self.with_context(active_test=False)
        domain = [
            ("departure_date", ">=", mstart),
            ("departure_date", "<", nstart),
        ]
        return self.env["hr.employee"].sudo().search_read(domain, [ESTADO_FIELD], limit=0)

    @api.model
    def _group_count_by_estado(self, records):
        """Group list of dicts by ESTADO_FIELD. Empty -> 'Sin Estado'."""
        counts = {}
        for rec in records:
            key = rec.get(ESTADO_FIELD) or _("Sin Estado")
            counts[key] = counts.get(key, 0) + 1
        return counts

    def action_compute(self):
        self.ensure_one()
        self.line_ids.unlink()

        mstart, nstart, mend = _month_bounds(self.target_month)
        prev_end = mstart - relativedelta(days=1)

        emp_inicio = self._employees_present_on(prev_end)
        inicio_by_estado = self._group_count_by_estado(emp_inicio)

        emp_fin = self._employees_present_on(mend)
        fin_by_estado = self._group_count_by_estado(emp_fin)

        emp_rot = self._employees_archived_in_month(mstart, nstart)
        rot_by_estado = self._group_count_by_estado(emp_rot)

        all_estados = set(inicio_by_estado.keys()) | set(fin_by_estado.keys()) | set(rot_by_estado.keys())

        Line = self.env["employee.rotation.report.line"].sudo()
        for estado in sorted(all_estados):
            inicio = inicio_by_estado.get(estado, 0)
            fin = fin_by_estado.get(estado, 0)
            rot = rot_by_estado.get(estado, 0)
            ingreso = (inicio + fin) / 2.0
            porcentaje = (rot / ingreso * 100.0) if ingreso else 0.0
            
            Line.create({
                "wizard_id": self.id,
                "estado": estado,
                "fecha": mend,      
                "inicio": inicio,
                "fin": fin,
                "rotacion": rot,
                "ingreso": ingreso,
                "porcentaje": porcentaje,
            })

        action = self.env.ref("hr_rotation_estado_report.action_employee_rotation_lines").read()[0]
        action["domain"] = [("wizard_id", "=", self.id)]
        return action


class EmployeeRotationReportLine(models.TransientModel):
    _name = "employee.rotation.report.line"
    _description = "Linea de Reporte de Rotacion por Estado"
    _order = "estado"

    wizard_id = fields.Many2one("employee.rotation.report.wizard", ondelete="cascade")

    estado = fields.Char(string="Estado del empleado", required=True, index=True)
    fecha = fields.Date(string="Fecha", required=True)  # <-- NUEVO
    inicio = fields.Integer(string="Inicio", required=True, default=0)
    fin = fields.Integer(string="Fin", required=True, default=0)
    rotacion = fields.Integer(string="Rotacion", required=True, default=0)
    ingreso = fields.Float(string="Ingreso", digits=(16, 2), required=True, default=0.0,
                           help="(Inicio + Fin) / 2")
    porcentaje = fields.Float(string="Porcentaje", digits=(16, 2), required=True, default=0.0,
                              help="Rotacion / Ingreso * 100")
    porcentaje_txt = fields.Char(string="Porcentaje", compute="_compute_porcentaje_txt")
   
    @api.depends("porcentaje")
    def _compute_porcentaje_txt(self):
        for rec in self:
            rec.porcentaje_txt = f"{(rec.porcentaje or 0.0):.2f} %"






