from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    x_studio_nuevo = fields.Char(
        string='Campo Nuevo',
        compute='_compute_x_studio_fields',
        store=True
    )
    quantity = fields.Float(
        compute='_compute_x_studio_fields',
        store=True
    )

    @api.depends('x_studio_cantidad')
    def _compute_x_studio_fields(self):
        for record in self:
            # Asegura que siempre se asignen los valores computados
            record.x_studio_nuevo = ''
            record.quantity = record.x_studio_cantidad or 0.0
