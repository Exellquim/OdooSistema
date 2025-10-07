from odoo import models

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_invoice_qty(self):
        """Ajusta la cantidad facturada en la OC según el subtotal vs precio OC"""
        self.ensure_one()
        qty = super()._get_invoice_qty()

        for line in self:
            for inv_line in line.invoice_lines.filtered(lambda l: l.move_id.move_type == "in_invoice"):
                # Tomar precio y subtotal de la factura
                price_factura = inv_line.price_unit
                subtotal_factura = inv_line.price_subtotal

                # Precio unitario de la OC
                price_oc = line.price_unit

                if price_oc > 0:
                    # Ajustar cantidad proporcional según el subtotal facturado
                    qty = subtotal_factura / price_oc

        return qty
