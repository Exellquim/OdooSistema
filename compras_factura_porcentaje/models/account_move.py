from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_invoice_line_from_po_line(self, line, invoice_id):
        """Ajusta la cantidad facturada como porcentaje del subtotal de la OC"""
        res = super()._prepare_invoice_line_from_po_line(line, invoice_id)

        subtotal_oc = line.price_unit * line.product_qty
        subtotal_factura = res.get("price_unit", 0) * res.get("quantity", 0)

        if subtotal_oc > 0 and subtotal_factura > 0:
            qty_calc = subtotal_factura / subtotal_oc * line.product_qty
            res["quantity"] = round(qty_calc, 4)

        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('price_unit', 'price_subtotal')
    def _onchange_price_unit_subtotal(self):
        """Mantener la cantidad en proporción al subtotal de la OC"""
        for line in self:
            if (
                line.move_id.move_type == "in_invoice"
                and line.purchase_line_id
            ):
                po_line = line.purchase_line_id
                subtotal_oc = po_line.price_unit * po_line.product_qty
                if subtotal_oc > 0 and line.price_unit:
                    subtotal_factura = line.price_unit * line.quantity
                    qty_calc = subtotal_factura / subtotal_oc * po_line.product_qty
                    line.quantity = round(qty_calc, 4)
