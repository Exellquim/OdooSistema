from odoo import models

class CustomAccountAgedReceivableHandler(models.AbstractModel):
    _inherit = "account.aged.receivable.report.handler"

    def _get_columns_name(self, options):
        # Llamamos al método original y agregamos una nueva columna
        columns = super()._get_columns_name(options)
        columns.append({'name': 'Impuesto total'})
        return columns

    def _get_lines(self, options, line_id=None):
        # Llamamos al original
        lines = super()._get_lines(options, line_id)
        Move = self.env['account.move']

        for line in lines:
            tax_amount = 0.0
            move_id = None
            line_id_val = line.get('id')

            # Detectar si la línea representa una factura (ej. "account.move,123")
            if isinstance(line_id_val, str) and line_id_val.startswith('account.move,'):
                try:
                    move_id = int(line_id_val.split(',')[1])
                except Exception:
                    move_id = None

            # Si es una factura, tomamos su total de impuestos firmados
            if move_id:
                move = Move.browse(move_id)
                if move.exists() and move.move_type in ('out_invoice', 'out_refund'):
                    tax_amount = move.amount_tax_signed

            # Agregar la columna de impuesto al final
            line.setdefault('columns', [])
            line['columns'].append({
                'name': self.env['account.report'].format_value(tax_amount),
                'class': 'number',
            })

        return lines
