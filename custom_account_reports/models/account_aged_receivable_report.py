from odoo import models, _

class AccountAgedReceivableReport(models.AbstractModel):
    _inherit = "account.aged.receivable.report"

    def _get_columns(self, options):
        """Agregamos una columna nueva 'Impuesto total' al reporte dinámico."""
        columns = super()._get_columns(options)
        columns.append(
            {
                'name': _('Impuesto total'),
                'class': 'number',
                'type': 'number',
                'sortable': True,
            }
        )
        return columns

    def _get_lines(self, options, line_id=None):
        """Calcula el impuesto total por factura."""
        lines = super()._get_lines(options, line_id)
        for line in lines:
            move_id = line.get('id')
            tax_total = 0.0
            if move_id and isinstance(move_id, int):
                move = self.env['account.move'].browse(move_id)
                if move.move_type in ['out_invoice', 'out_refund']:
                    tax_total = move.amount_tax_signed
            # Agregar la columna al final
            line['columns'].append({'name': tax_total, 'no_format': tax_total})
        return lines
