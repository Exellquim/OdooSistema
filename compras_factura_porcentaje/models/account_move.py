from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.price_subtotal')
    def _compute_qty_invoiced(self):
        """
        Permite facturar parcialmente hasta completar el total de la OC
        Solo aplica para facturas de proveedores (in_invoice).
        El qty_invoiced reflejará el porcentaje facturado (0.0 - 1.0)
        """
        super()._compute_qty_invoiced()

        for line in self:
            # Total esperado en la OC (por línea)
            total_oc = line.price_unit * line.product_qty

            # Total facturado únicamente en facturas de proveedores válidas
            total_facturado = sum(
                inv_line.price_subtotal
                for inv_line in line.invoice_lines
                if inv_line.move_id.state != 'cancel'
                and inv_line.move_id.move_type == 'in_invoice'
            )

            if total_facturado > 0 and total_oc > 0:
                # Calcular porcentaje facturado
                porcentaje = total_facturado / total_oc
                # No permitir que supere 1 (100%)
                line.qty_invoiced = min(porcentaje, 1.0)
            else:
                line.qty_invoiced = 0.0
