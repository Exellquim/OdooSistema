from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.price_subtotal')
    def _compute_qty_invoiced(self):
        """Extiende el cálculo estándar y lo ajusta a porcentaje"""
        super()._compute_qty_invoiced()  

        for line in self:
            total_oc = line.price_unit * line.product_qty

            total_facturado = sum(
                inv_line.price_subtotal
                for inv_line in line.invoice_lines
                if inv_line.move_id.state != 'cancel'
                and inv_line.move_id.move_type == 'in_invoice'
            )

            if total_oc > 0 and total_facturado > 0:
                porcentaje = total_facturado / total_oc
                line.qty_invoiced = round(porcentaje, 4)
