from odoo import models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def create(self, vals_list):
        records = super().create(vals_list)
        for line in records:
            if (
                line.move_id.move_type == "in_invoice"
                and line.purchase_line_id
                and line.price_unit
                and line.price_subtotal
            ):
                try:
                    new_qty = line.price_subtotal / line.price_unit
                    line.quantity = round(new_qty, 4)  # redondeo para evitar decimales largos
                except ZeroDivisionError:
                    pass
        return records


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for move in self:
            if move.move_type == "in_invoice":
                for line in move.invoice_line_ids.filtered(lambda l: l.purchase_line_id):
                    if line.price_unit and line.price_subtotal:
                        try:
                            new_qty = line.price_subtotal / line.price_unit
                            line.quantity = round(new_qty, 4)
                        except ZeroDivisionError:
                            pass
        return super().action_post()
