from odoo import models, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_account_move_line(self, move):
        """
        Ajusta la línea de factura para facturación parcial:
        - Cantidad proporcional
        - Precio unitario = el de la OC (nunca cambia)
        - Subtotal proporcional
        """
        res = super()._prepare_account_move_line(move)

        if move.move_type == 'in_invoice' and self.product_qty > 0 and self.price_unit > 0:
            total_oc = self.price_unit * self.product_qty

            # Total ya facturado
            total_facturado = sum(
                inv_line.price_subtotal
                for inv_line in self.invoice_lines
                if inv_line.move_id.state != 'cancel'
                and inv_line.move_id.move_type == 'in_invoice'
            )

            pendiente = total_oc - total_facturado
            if pendiente > 0:
                # Cantidad proporcional al pendiente
                qty_pendiente = pendiente / self.price_unit

                res.update({
                    "quantity": qty_pendiente,
                    "price_unit": self.price_unit,  # siempre el de la OC
                })
        return res
