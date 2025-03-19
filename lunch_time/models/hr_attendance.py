from odoo import models, fields, api

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    hora_de_comida = fields.Datetime(string="Hora de Comida")
    regreso_de_comida = fields.Datetime(string="Regreso de Comida")


