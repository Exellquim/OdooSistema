from odoo import models, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for line in records:
            if (
                line.move_id.move_type == "in_invoice"
                and line.purchase_line_id
                and line.price_unit
                and line.move_id.purchase_vendor_bill_id
            ):
                po_line = line.purchase_line_id
                total_po = po_line.price_unit * po_line.product_qty
                total_invoiced = sum(line.mapped("purchase_line_id.invoice_lines.price_subtotal"))
                pendiente = total_po - total_invoiced

                if line.price_subtotal and line.price_subtotal < po_line.price_unit:
                    line.quantity = line.price_subtotal / line.price_unit
        return records


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for move in self:
            if move.move_type == "in_invoice":
                for line in move.invoice_line_ids.filtered(lambda l: l.purchase_line_id):
                    if line.price_unit and line.price_subtotal:
                        qty_calc = line.price_subtotal / line.price_unit
                        if 0 < qty_calc < line.quantity:
                            line.quantity = round(qty_calc, 4)
        return super().action_post()
