from odoo import models

class AccountAgedPartnerReport(models.AbstractModel):
    _inherit = "account.aged.partner"

    def _get_columns_name(self, options):
        columns = super()._get_columns_name(options)
        columns.append({'name': 'Impuesto total'})
        return columns

    def _get_lines(self, options, line_id=None):
        lines = super()._get_lines(options, line_id)
        for line in lines:
            move_id = line.get('id')
            tax_amount = 0.0
            if move_id and isinstance(move_id, int):
                move = self.env['account.move'].browse(move_id)
                if move.move_type in ['out_invoice', 'out_refund']:
                    tax_amount = move.amount_tax_signed
            line['columns'].append({'name': f"{tax_amount:,.2f}"})
        return lines
