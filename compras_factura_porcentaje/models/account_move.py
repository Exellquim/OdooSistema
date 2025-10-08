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
        - qty_invoiced = cantidad proporcional facturada
        - porcentaje_invoiced = % del total facturado
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
                line.qty_invoiced = min(line.product_qty * porcentaje, line.product_qty)
            else:
                line.porcentaje_invoiced = 0.0
                line.qty_invoiced = 0.0


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_invoiceable_lines(self, final=False):
        """
        Permitir facturación parcial basada en porcentaje,
        aunque la política del producto sea 'cantidad recibida'.
        """
        res = super()._get_invoiceable_lines(final=final)
        for order in self:
            for line in order.order_line:
                # Si la línea aún no está facturada por completo, la hacemos facturable
                if line.product_id and line.qty_invoiced < line.product_qty:
                    if line not in res:
                        res |= line
        return res
