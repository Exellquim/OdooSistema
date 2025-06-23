from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    nuevo = fields.Char(string='Campo Nuevo', store=True)
    cantidad = fields.Float(store=True, default=0.0)

    @api.onchange('cantidad')
    def _onchange_cantidad(self):
        for record in self:
            tracking = record.product_id.tracking
            move_lines_with_lot = record.move_line_ids.filtered(lambda l: l.lot_id)

            if tracking in ['lot', 'serial']:
                if move_lines_with_lot:
                    # Si hay lote, actualiza la línea y también el movimiento
                    move_lines_with_lot[0].qty_done = record.cantidad
                    record.quantity = record.cantidad
                else:
                    # Si no hay lote, bloquear cantidad
                    record.quantity = 0.0
            else:
                # Si no requiere lote, actualiza ambas cantidades
                record.quantity = record.cantidad
                for ml in record.move_line_ids:
                    ml.qty_done = record.cantidad
