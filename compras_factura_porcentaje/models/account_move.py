from odoo import models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_invoice_line_from_po_line(self, line, invoice_id):
        """Personaliza la creación de líneas de factura desde la OC"""
        res = super()._prepare_invoice_line_from_po_line(line, invoice_id)
   
        if res.get("price_unit") and res.get("price_subtotal"):
            try:
                qty_calc = res["price_subtotal"] / res["price_unit"]
                if 0 < qty_calc < res.get("quantity", 1):
                    res["quantity"] = round(qty_calc, 4)
            except ZeroDivisionError:
                pass
        return res
