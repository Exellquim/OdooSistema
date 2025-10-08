from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    porcentaje_invoiced = fields.Float(
        string="Porcentaje Facturado",
        compute="_compute_qty_invoiced",
        store=False
    )

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.price_subtotal')
    def _compute_qty_invoiced(self):
        """
        - qty_invoiced = cantidad proporcional facturada (ej: 0.5 de 1)
        - porcentaje_invoiced = % del total facturado (ej: 0.5)
        """
        super()._compute_qty_invoiced()

        for line in self:
            total_oc = line.price_unit * line.product_qty
            total_facturado = sum(
                inv_line.price_subtotal
                for inv_line in line.invoice_lines
                if inv_line.move_id.state != 'cancel'
                and inv_line.move_id.move_type == 'in_invoice'
            )

            if total_facturado > 0 and total_oc > 0 and line.price_unit > 0:
                porcentaje = total_facturado / total_oc
                line.porcentaje_invoiced = round(porcentaje, 4)

                # cantidad facturada proporcional
                qty_facturada = line.product_qty * porcentaje
                line.qty_invoiced = min(qty_facturada, line.product_qty)
            else:
                line.porcentaje_invoiced = 0.0
                line.qty_invoiced = 0.0
