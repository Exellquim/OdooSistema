from odoo import models, fields
from odoo.tools import float_is_zero

class CustomStockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        # Filtrar los picking en estado draft
        draft_picking = self.filtered(lambda p: p.state == 'draft')
        draft_picking.action_confirm()

        # Recorrer los movimientos de los picking filtrados
        for move in draft_picking.move_ids:
            # Si la cantidad es cero y product_uom_qty no lo es, se asigna 0.0 a quantity
            if float_is_zero(move.quantity, precision_rounding=move.product_uom.rounding) and\
               not float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                move.quantity = 0.0  # Asignar 0.0 en lugar de product_uom_qty

        # Comprobaciones de consistencia
        if not self.env.context.get('skip_sanity_check', False):
            self._sanity_check()

        # Suscribirse al mensaje del usuario actual
        self.message_subscribe([self.env.user.partner_id.id])

        # Ejecutar los wizards de pre-validación
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        return True
