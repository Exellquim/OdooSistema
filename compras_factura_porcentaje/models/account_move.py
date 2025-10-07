from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_invoice_line_from_po_line(self, line, invoice_id):
        """Ajusta cantidad proporcional manteniendo precio ingresado en factura"""
        res = super()._prepare_invoice_line_from_po_line(line, invoice_id)

        price_oc = line.price_unit
        qty_oc = line.product_qty
        price_factura = res.get("price_unit", 0)

        if price_oc > 0 and price_factura > 0:
            # calcular proporción según precio facturado vs OC
            factor = price_factura / price_oc
            res["quantity"] = round(qty_oc * factor, 4)

        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        """Recalcula cantidad cuando se cambia el precio, tomando como referencia la OC"""
        for line in self:
            if (
                line.move_id.move_type == "in_invoice"
                and line.purchase_line_id
            ):
                po_line = line.purchase_line_id
                price_oc = po_line.price_unit
                qty_oc = po_line.product_qty
                price_factura = line.price_unit

                if price_oc > 0 and price_factura > 0:
                    factor = price_factura / price_oc
                    line.quantity = round(qty_oc * factor, 4)
