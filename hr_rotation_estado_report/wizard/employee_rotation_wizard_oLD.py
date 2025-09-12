from datetime import date, datetime, timedelta
@api.model
def _group_count_by_estado(self, records):
"""Agrupa una lista de dicts por ESTADO_FIELD, valores vacíos → 'Sin Estado'."""
counts = {}
for rec in records:
key = rec.get(ESTADO_FIELD) or _('Sin Estado')
counts[key] = counts.get(key, 0) + 1
return counts


def action_compute(self):
self.ensure_one()
# Limpiar resultados previos
self.line_ids.unlink()


# Mes objetivo
mstart, nstart, mend = _month_bounds(self.target_month)
# Mes previo (para INICIO)
prev_end = mstart - relativedelta(days=1)


# Presencia al cierre del mes previo (INICIO)
emp_inicio = self._employees_present_on(prev_end)
inicio_by_estado = self._group_count_by_estado(emp_inicio)


# Presencia al cierre del mes objetivo (FIN)
emp_fin = self._employees_present_on(mend)
fin_by_estado = self._group_count_by_estado(emp_fin)


# Archivados dentro del mes (ROTACIÓN)
emp_rot = self._employees_archived_in_month(mstart, nstart)
rot_by_estado = self._group_count_by_estado(emp_rot)


# Unión de claves (estados)
all_estados = set(inicio_by_estado.keys()) | set(fin_by_estado.keys()) | set(rot_by_estado.keys())


Line = self.env['employee.rotation.report.line'].sudo()
for estado in sorted(all_estados):
inicio = inicio_by_estado.get(estado, 0)
fin = fin_by_estado.get(estado, 0)
rot = rot_by_estado.get(estado, 0)
ingreso = (inicio + fin) / 2.0
porcentaje = (rot / ingreso * 100.0) if ingreso else 0.0


Line.create({
'wizard_id': self.id,
'estado': estado,
'inicio': inicio,
'fin': fin,
'rotacion': rot,
'ingreso': ingreso,
'porcentaje': porcentaje,
})


# Abrir resultados (tabla + gráfica)
action = self.env.ref('hr_rotation_estado_report.action_employee_rotation_lines').read()[0]
action['domain'] = [('wizard_id', '=', self.id)]
return action




class EmployeeRotationReportLine(models.TransientModel):
_name = 'employee.rotation.report.line'
_description = 'Línea de Reporte de Rotación por Estado'
_order = 'estado'


wizard_id = fields.Many2one('employee.rotation.report.wizard', ondelete='cascade')


estado = fields.Char(string='Estado del empleado', required=True, index=True)
inicio = fields.Integer(string='Inicio', required=True, default=0)
fin = fields.Integer(string='Fin', required=True, default=0)
rotacion = fields.Integer(string='Rotación', required=True, default=0)
ingreso = fields.Float(string='Ingreso', digits=(16, 2), required=True, default=0.0,
help='(Inicio + Fin) / 2')
porcentaje = fields.Float(string='Porcentaje', digits=(16, 2), required=True, default=0.0,
help='Rotación / Ingreso * 100')