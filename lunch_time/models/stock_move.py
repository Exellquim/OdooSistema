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

    @api.depends('cantidad')
    def _compute_quantity(self):
        for record in self:
            if record.state not in ('done', 'cancel'):
                record.quantity = record.cantidad

