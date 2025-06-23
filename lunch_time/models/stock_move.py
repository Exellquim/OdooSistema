from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    nuevo = fields.Char(
        string='Campo Nuevo',
        compute='_compute_x_studio_fields',
        store=True
    )
    cantidad = fields.Float(
        compute='_compute_x_studio_fields',
        store=True
    )

    @api.depends('cantidad')
    def _compute_x_studio_fields(self):
        for record in self:
            # Asegura que siempre se asignen los valores computados
            record.nuevo = ''
            record.quantity = record.cantidad or 0.0
