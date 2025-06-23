from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    cantidad = fields.Float(string='Cantidad Nueva', store=True, default=0.0)
    nuevo = fields.Char(string='Campo Nuevo', store=True)

    @api.onchange('cantidad')
    def _onchange_cantidad(self):
        for move in self:
            cantidad_valor = move.cantidad or 0.0
            move.quantity = cantidad_valor  # visible en vista

            tracking = move.product_id.tracking
            lot_line = move.move_line_ids.filtered(lambda l: l.lot_id)

            # Producto con rastreo: solo actualiza qty_done si ya hay lote
            if tracking in ['lot', 'serial']:
                if lot_line:
                    lot_line[0].qty_done = cantidad_valor
            else:
                # Sin rastreo, se puede llenar qty_done directo
                for ml in move.move_line_ids:
                    ml.qty_done = cantidad_valor
