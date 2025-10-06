from odoo import api, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('price_unit', 'price_subtotal')
    def _onchange_price_subtotal_adjust_qty(self):
        """
        Cuando se edita el subtotal en la factura,
        recalcula la cantidad en base al precio unitario
        de la orden de compra vinculada.
        """
        for line in self:
            if line.move_id.move_type in ['in_invoice'] and line.purchase_line_id:
                price_unit = line.price_unit
                subtotal = line.price_subtotal
                if price_unit and subtotal:
                    new_qty = subtotal / price_unit
                    line.quantity = new_qty

