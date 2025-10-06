from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_invoice_line_from_po_line(self, line, invoice_id):
        """Ajusta la cantidad facturada manteniendo el precio unitario ingresado"""
        res = super()._prepare_invoice_line_from_po_line(line, invoice_id)

        subtotal_oc = line.price_unit * line.product_qty
        subtotal_factura = res.get("price_unit", 0) * res.get("quantity", 0)

        if subtotal_oc > 0 and subtotal_factura > 0:
            qty_calc = subtotal_factura / subtotal_oc * line.product_qty
            res["quantity"] = round(qty_calc, 4)

        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('price_unit', 'quantity')
    def _onchange_price_unit_quantity(self):
        """Si el usuario cambia el precio, recalcula la cantidad proporcional al subtotal"""
        for line in self:
            if (
                line.move_id.move_type == "in_invoice"
                and line.purchase_line_id
            ):
                po_line = line.purchase_line_id
                subtotal_oc = po_line.price_unit * po_line.product_qty

                subtotal_factura = line.price_unit * line.quantity

                if subtotal_oc > 0 and subtotal_factura > 0:
                    qty_calc = subtotal_factura / subtotal_oc * po_line.product_qty
                    line.quantity = round(qty_calc, 4)
