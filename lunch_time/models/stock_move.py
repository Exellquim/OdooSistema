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


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('move_ids.cantidad')
    def _compute_move_quantities(self):
        for picking in self:
            for move in picking.move_ids:
                move.nuevo = ''
                if move.state not in ('done', 'cancel'):
                    move.quantity = move.cantidad or 0.0

