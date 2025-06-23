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
            if record.product_id.tracking in ['lot', 'serial'] and not record.lot_ids:
                # Si el producto requiere lote y aún no se capturó, no asignar
                record.quantity = 0.0
            else:
                record.quantity = record.cantidad or 0.0


