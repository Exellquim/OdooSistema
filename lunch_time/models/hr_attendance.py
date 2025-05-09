from odoo import models, fields, api

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    hora_de_comida = fields.Datetime(string="Hora de Comida")
    regreso_de_comida = fields.Datetime(string="Regreso de Comida")
    registro = fields.Date(string="Registro fecha", compute="_compute_registro", store=True)

    @api.depends('check_in')
    def _compute_registro(self):
        for record in self:
            record.registro = record.check_in.date() if record.check_in else False

class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_type = fields.Selection(
        selection_add=[('resultado', 'Resultado')],
        ondelete={'resultado': 'set default'}
    )


