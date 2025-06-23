from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    nuevo = fields.Char(string='Campo Nuevo', store=True)
    cantidad = fields.Float(store=True, default=0.0)

    def asignar_cantidad_a_lote(self):
        for move in self:
            if move.product_id.tracking in ['lot', 'serial']:
                lot_line = move.move_line_ids.filtered(lambda l: l.lot_id)
                if not lot_line:
                    raise ValidationError("Debes capturar primero un lote en operaciones detalladas.")
                # Asigna la cantidad ingresada al lote
                lot_line[0].qty_done = move.cantidad
                move.quantity = move.cantidad
            else:
                # Si el producto no tiene seguimiento, puedes asignar directamente
                move.quantity = move.cantidad
