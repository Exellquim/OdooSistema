from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    nuevo = fields.Char(string='Campo Nuevo', store=True)
    cantidad = fields.Float(string='Cantidad Nueva', store=True, default=0.0)

    @api.onchange('cantidad')
    def _onchange_cantidad(self):
        for move in self:
            move.quantity = move.cantidad  # Actualiza campo de vista
            move_lines = move.move_line_ids
            if move_lines:
                # Si ya hay una línea, solo actualizamos qty_done
                move_lines[0].qty_done = move.cantidad
            else:
                # Si no hay línea aún, se crea en operaciones detalladas, no hacemos nada
                pass
