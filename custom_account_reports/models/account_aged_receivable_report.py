from odoo import models, _

class AccountAgedReceivableReport(models.AbstractModel):
    _inherit = "account.aged.receivable.report"

    # 1️⃣ Agregamos la columna "Impuesto total"
    def _get_columns(self, options):
        columns = super()._get_columns(options)
        columns.append(
            {
                'name': _('Impuesto total'),
                'expression_label': 'Impuesto total',
                'class': 'number',
                'type': 'number',
                'sortable': True,
            }
        )
        return columns

    # 2️⃣ Calculamos el monto de impuesto total de cada factura
    def _get_lines(self, options, line_id=None):
        lines = super()._get_lines(options, line_id)
        for line in lines:
            move_id = line.get('id')
            tax_total = 0.0
            if move_id and isinstance(move_id, int):
                move = self.env['account.move'].browse(move_id)
                if move.move_type in ['out_invoice', 'out_refund']:
                    tax_total = move.amount_tax_signed
            # Añadir la columna (debe coincidir con el orden de columnas del reporte)
            if 'columns' in line:
                line['columns'].append({'name': self.format_value(tax_total), 'no_format': tax_total})
        return lines

    # 3️⃣ Ajuste de plantillas (asegura que la nueva columna se renderice)
    def _get_templates(self):
        templates = super()._get_templates()
        templates['main_table_header_template'] = 'account_reports.main_table_header_template'
        templates['main_table_row_template'] = 'account_reports.main_table_row_template'
        return templates
