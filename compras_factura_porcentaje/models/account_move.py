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

    def _prepare_account_move_line(self, move=False):
        """
        Facturación parcial desde OC:
        - cantidad proporcional pendiente
        - precio unitario fijo = precio de la OC
        Solo aplica en facturas de proveedor (in_invoice)
        """
        res = super()._prepare_account_move_line(move)

        if move and move.move_type == 'in_invoice' and self.price_unit > 0:
            total_oc = self.price_unit * self.product_qty

            # Total ya facturado
            total_facturado = sum(
                inv_line.price_subtotal
                for inv_line in self.invoice_lines
                if inv_line.move_id.state != 'cancel'
                and inv_line.move_id.move_type == 'in_invoice'
            )

            pendiente = total_oc - total_facturado
            if pendiente > 0:
                qty_pendiente = pendiente / self.price_unit
                res.update({
                    "quantity": qty_pendiente,
                    "price_unit": self.price_unit,
                })
        return res


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_invoiceable_lines(self, final=False):
        """
        Permitir facturación parcial basada en porcentaje,
        aunque la política de facturación del producto sea 'cantidad recibida'.
        """
        res = super()._get_invoiceable_lines(final=final)
        for order in self:
            for line in order.order_line:
                if line.product_id and line.qty_invoiced < line.product_qty:
                    if line not in res:
                        res |= line
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('price_unit')
    def _onchange_price_unit_keep_oc_price(self):
        """
        Si en una factura de proveedor (in_invoice) el usuario cambia el price_unit:
        - recalcula la cantidad proporcional
        - restablece el precio unitario al de la OC
        """
        for line in self:
            move = line.move_id
            purchase_line = line.purchase_line_id

            if move.move_type == 'in_invoice' and purchase_line and purchase_line.price_unit > 0:
                price_oc = purchase_line.price_unit

                # cantidad proporcional = nuevo precio escrito ÷ precio OC
                qty_proporcional = line.price_unit / price_oc

                line.quantity = qty_proporcional
                line.price_unit = price_oc
