from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_invoice_line_from_po_line(self, line, invoice_id):
        """Ajusta la cantidad facturada según el precio unitario de la OC"""
        res = super()._prepare_invoice_line_from_po_line(line, invoice_id)

        res["price_unit"] = line.price_unit  

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
        """Corrige la cantidad según el subtotal de la OC, manteniendo el precio unitario de la OC"""
        for line in self:
            if (
                line.move_id.move_type == "in_invoice"
                and line.purchase_line_id
            ):
                po_line = line.purchase_line_id
                price_oc = po_line.price_unit
                subtotal_oc = price_oc * po_line.product_qty

                subtotal_factura = line.price_unit * line.quantity

                line.price_unit = price_oc

                if subtotal_oc > 0 and subtotal_factura > 0:
                    qty_calc = subtotal_factura / subtotal_oc * po_line.product_qty
                    line.quantity = round(qty_calc, 4)
