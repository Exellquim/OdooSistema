from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    porcentaje_invoiced = fields.Float(
        string="Porcentaje Facturado",
        compute="_compute_porcentaje_invoiced",
        store=False   # <--- no crea columna en DB
    )

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.price_subtotal')
    def _compute_porcentaje_invoiced(self):
        """Calcula el % facturado solo de forma informativa"""
        for line in self:
            total_oc = line.price_unit * line.product_qty
            total_facturado = sum(
                inv_line.price_subtotal
                for inv_line in line.invoice_lines
                if inv_line.move_id.state != 'cancel'
                and inv_line.move_id.move_type == 'in_invoice'
            )
            if total_facturado > 0 and total_oc > 0:
                line.porcentaje_invoiced = round(total_facturado / total_oc, 4)
            else:
                line.porcentaje_invoiced = 0.0
