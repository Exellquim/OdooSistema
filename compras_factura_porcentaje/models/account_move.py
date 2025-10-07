from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_invoiced = fields.Float(
        string="Cantidad facturada",
        compute="_compute_qty_invoiced",
        store=True,
        readonly=True
    )

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.price_subtotal')
    def _compute_qty_invoiced(self):
        """Calcular qty_invoiced como el porcentaje facturado vs total OC"""
        for line in self:
            qty = 0.0
            total_oc = line.price_unit * line.product_qty

            # sumar subtotales de facturas confirmadas (posted)
            total_facturado = sum(
                inv_line.price_subtotal
                for inv_line in line.invoice_lines
                if inv_line.move_id.state != 'cancel'
                and inv_line.move_id.move_type == 'in_invoice'
            )

            if total_oc > 0 and total_facturado > 0:
                qty = total_facturado / total_oc

            line.qty_invoiced = round(qty, 4)
