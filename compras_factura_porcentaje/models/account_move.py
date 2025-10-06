from odoo import models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @classmethod
    def create(cls, vals_list):
        records = super().create(vals_list)
        for line in records:
            if (
                line.move_id.move_type == "in_invoice"
                and line.purchase_line_id
                and line.price_unit
                and line.price_subtotal
            ):
                new_qty = line.price_subtotal / line.price_unit
                line.quantity = new_qty
        return records


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for move in self:
            if move.move_type == "in_invoice":
                for line in move.invoice_line_ids.filtered(lambda l: l.purchase_line_id):
                    if line.price_unit and line.price_subtotal:
                        new_qty = line.price_subtotal / line.price_unit
                        line.quantity = new_qty
        return super().action_post()
