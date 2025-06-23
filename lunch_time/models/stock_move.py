from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    nuevo = fields.Char(
        string='Campo Nuevo',
        store=True
    )
    cantidad = fields.Float(
        store=True,
        default=0.0
    )

    @api.onchange('cantidad')
    def _onchange_cantidad(self):
        for record in self:
            tracking = record.product_id.tracking
            move_lines_with_lot = record.move_line_ids.filtered(lambda l: l.lot_id)

            if tracking in ['lot', 'serial'] and not move_lines_with_lot:
                # Producto requiere lote y no hay ninguno capturado
                record.quantity = 0.0
            else:
                record.quantity = record.cantidad or 0.0
