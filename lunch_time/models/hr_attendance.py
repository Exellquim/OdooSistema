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


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('picking_type_id'):  # Solo afecta a movimientos de recepción
                vals['quantity'] = 0.0
        return super().create(vals_list)

        return True


class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_type = fields.Selection(
        selection_add=[('resultado', 'Resultado')],
        ondelete={'resultado': 'cascade'}  # Elimina registros con esta opción al desinstalar
    )



