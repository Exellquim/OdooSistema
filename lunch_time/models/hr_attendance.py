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

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        for move_vals in res:
            move_vals['product_uom_qty'] = 0.0  # Forzar a 0 la cantidad solicitada en la recepción
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('picking_type_id'):  # Solo afecta a movimientos de recepción
                vals['quantity'] = 0.0
        return super().create(vals_list)

        return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        for move_vals in res:
            move_vals['quantity'] = 0.0  # Forzar la cantidad a 0 antes de crear el movimiento
        return res


class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_type = fields.Selection(
        selection_add=[('resultado', 'Resultado')],
        ondelete={'resultado': 'cascade'}  # Elimina registros con esta opción al desinstalar
    )



