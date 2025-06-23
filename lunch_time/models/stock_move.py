from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    nuevo = fields.Char(string='Campo Nuevo', store=True)
    cantidad = fields.Float(string='Cantidad Nueva', store=True, default=0.0)

    @api.onchange('cantidad')
    def _onchange_cantidad(self):
        for move in self:
            move.quantity = move.cantidad or 0.0  # Siempre actualizar el campo quantity visible

            tracking = move.product_id.tracking
            has_lot = move.move_line_ids.filtered(lambda l: l.lot_id)

            if tracking in ['lot', 'serial']:
                if has_lot:
                    # Solo actualiza qty_done si ya hay lote capturado
                    has_lot[0].qty_done = move.cantidad or 0.0
                # Si no hay lote, no hacer nada → Odoo lo validará normalmente y mostrará el error de lote faltante
            else:
                # Producto no requiere lote, se puede asignar libremente
                for ml in move.move_line_ids:
                    ml.qty_done = move.cantidad or 0.0
