from odoo import models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_invoice_line_from_po_line(self, line, invoice_id):
        """Ajusta la cantidad facturada como porcentaje del subtotal de la OC"""
        res = super()._prepare_invoice_line_from_po_line(line, invoice_id)

        subtotal_oc = line.price_unit * line.product_qty

        subtotal_factura = res.get("price_unit", 0) * res.get("quantity", 0)

        if subtotal_oc > 0 and subtotal_factura > 0:
            qty_calc = subtotal_factura / subtotal_oc * line.product_qty
            res["quantity"] = qty_calc

        return res

