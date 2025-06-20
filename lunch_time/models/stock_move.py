from odoo import models, fields
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    cantidad = fields.Float(string="Cantidad para validar")
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            for move in picking.move_ids_without_package:
                if move.cantidad <= 0:
                    raise ValidationError(f"La línea del producto '{move.product_id.display_name}' tiene cantidad en cero. No se puede validar.")
                move.quantity_done = move.cantidad  # copiar el valor a quantity_done

        return super().button_validate()
