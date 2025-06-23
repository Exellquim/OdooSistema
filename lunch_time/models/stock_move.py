from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    nuevo = fields.Char(string='Campo Nuevo', store=True)
    cantidad = fields.Float(store=True, default=0.0)

    @api.onchange('cantidad')
    def _onchange_cantidad(self):
        for record in self:
            tracking = record.product_id.tracking

            # Filtrar línea con lote capturado
            lot_line = record.move_line_ids.filtered(lambda l: l.lot_id)

            if tracking in ['lot', 'serial']:
                if lot_line:
                    # Hay lote → actualizamos qty_done en la línea con lote
                    lot_line[0].qty_done = record.cantidad
                    record.quantity = record.cantidad
                else:
                    # Producto requiere lote pero no se ha capturado → bloquear
                    record.quantity = 0.0
            else:
                # Producto no requiere lote
                record.quantity = record.cantidad
