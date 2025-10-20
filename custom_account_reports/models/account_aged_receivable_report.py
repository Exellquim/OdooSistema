from odoo import models

class AccountAgedPartnerReport(models.AbstractModel):
    _inherit = "account.aged.partner"

    def _get_columns_name(self, options):
        columns = super()._get_columns_name(options)
        columns.append({'name': 'Impuesto total'})
        return columns

    def _get_lines(self, options, line_id=None):
        lines = super()._get_lines(options, line_id)
        date_to = (options or {}).get('date', {}).get('date_to')
        Move = self.env['account.move']

        for line in lines:
            tax_amount = 0.0
            move_id = None
            lid = line.get('id')

            if isinstance(lid, int):
                move_id = lid
            elif isinstance(lid, str):
                if lid.startswith('move_'):
                    try:
                        move_id = int(lid.split('_')[-1])
                    except Exception:
                        pass
                elif ',' in lid:
                    model_name, _, rec_id = lid.partition(',')
                    if model_name in ('account.move', 'move', 'account.move.line'):
                        try:
                            move_id = int(rec_id)
                        except Exception:
                            pass

            if move_id:
                move = Move.browse(move_id)
                if move.exists() and move.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):
                    tax_amount = move.amount_tax_signed
            elif line.get('partner_id'):
                domain = [
                    ('partner_id', '=', line['partner_id']),
                    ('state', '=', 'posted'),
                    ('move_type', 'in', ('out_invoice', 'out_refund')),
                ]
                if date_to:
                    domain.append(('invoice_date', '<=', date_to))
                moves = Move.search(domain)
                tax_amount = sum(m.amount_tax_signed for m in moves)

            line.setdefault('columns', [])
            line['columns'].append({'name': self.format_value(tax_amount), 'class': 'number'})
        return lines
