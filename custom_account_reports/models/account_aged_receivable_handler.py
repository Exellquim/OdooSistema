from odoo import models

class CustomAccountAgedReceivableHandler(models.AbstractModel):
    _inherit = "account.aged.receivable.report.handler"

    def _get_columns_name(self, options):
        """Agrega una nueva columna 'Impuesto total' al reporte."""
        columns = super()._get_columns_name(options)
        columns.append({'name': 'Impuesto total'})
        return columns

    def _get_lines(self, options, line_id=None):
        """Agrega los valores de impuesto total por factura o por partner."""
        lines = super()._get_lines(options, line_id)
        Move = self.env['account.move']

        for line in lines:
            tax_amount = 0.0
            move_id = None
            line_id_val = line.get('id')

            if isinstance(line_id_val, str) and line_id_val.startswith('account.move,'):
                try:
                    move_id = int(line_id_val.split(',')[1])
                except Exception:
                    move_id = None

            if move_id:
                move = Move.browse(move_id)
                if move.exists() and move.move_type in ('out_invoice', 'out_refund'):
                    tax_amount = move.amount_tax_signed

            elif isinstance(line_id_val, str) and line_id_val.startswith('partner_'):
                try:
                    partner_id = int(line_id_val.split('_')[1])
                    domain = [
                        ('partner_id', '=', partner_id),
                        ('state', '=', 'posted'),
                        ('move_type', 'in', ('out_invoice', 'out_refund')),
                    ]
                    date_to = (options or {}).get('date', {}).get('date_to')
                    if date_to:
                        domain.append(('invoice_date', '<=', date_to))

                    moves = Move.search(domain)
                    tax_amount = sum(m.amount_tax_signed for m in moves)
                except Exception:
                    tax_amount = 0.0

            # Agregar columna al final
            line.setdefault('columns', [])
            line['columns'].append({
                'name': self.env['account.report'].format_value(tax_amount),
                'class': 'number',
            })

        return lines


