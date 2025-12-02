from odoo import models, fields
import base64
import io
import xlsxwriter


class FacturasPagosExcelWizard(models.TransientModel):
    _name = 'facturas.pagos.excel.wizard'
    _description = 'Exportar reporte de facturas con pagos reales'

    date_start = fields.Date(string='Fecha de pago desde')
    date_end = fields.Date(string='Fecha de pago hasta')
    file = fields.Binary('Archivo Excel', readonly=True)
    file_name = fields.Char('Nombre del archivo', default='facturas_con_pagos.xlsx', readonly=True)

    def exportar_excel(self):
        self.ensure_one()
        payment_domain = []
        if self.date_start:
            payment_domain.append(('date', '>=', self.date_start))
        if self.date_end:
            payment_domain.append(('date', '<=', self.date_end))

        payments = self.env['account.payment'].search(payment_domain)

        payment_moves = payments.mapped('move_id')
        move_lines = payment_moves.mapped('line_ids')

        matched = move_lines.mapped('matched_debit_ids') | move_lines.mapped('matched_credit_ids')

        invoice_moves = (
            matched.mapped('debit_move_id.move_id') |
            matched.mapped('credit_move_id.move_id')
        )

        invoices = invoice_moves.filtered(
            lambda m: m.move_type in ('out_invoice', 'out_refund') and m.state == 'posted'
        )

        if not invoices:
            self.write({
                'file': False,
                'file_name': 'sin_facturas.xlsx',
            })
            return {'type': 'ir.actions.act_window_close'}

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Facturas con Pagos')

        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})
        datefmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        headers = [
            'Factura', 'UUID', 'Cliente', 'RFC',
            'Fecha Factura', 'Moneda', 'Total Factura',
            'Pago Acumulado', 'Saldo Restante',
        ]

        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)

        row = 1

        for inv in invoices:

            receivables = inv.line_ids.filtered(
                lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')
            )

            matched_parts = (
                receivables.mapped('matched_debit_ids') |
                receivables.mapped('matched_credit_ids')
            )

            pago_acumulado = 0.0

            for m in matched_parts:
                if m.debit_move_id.move_id.id == inv.id:
                    pago_acumulado += abs(m.credit_amount_currency or m.credit_amount or 0.0)
                else:
                    pago_acumulado += abs(m.debit_amount_currency or m.debit_amount or 0.0)

            saldo_restante = inv.amount_total - pago_acumulado

            c = 0
            sheet.write(row, c, inv.name); c += 1
            sheet.write(row, c, inv.l10n_mx_edi_cfdi_uuid or ''); c += 1
            sheet.write(row, c, inv.partner_id.name); c += 1
            sheet.write(row, c, inv.partner_id.vat or ''); c += 1
            sheet.write_datetime(row, c, fields.Datetime.to_datetime(inv.invoice_date), datefmt); c += 1
            sheet.write(row, c, inv.currency_id.name); c += 1
            sheet.write_number(row, c, inv.amount_total, money); c += 1
            sheet.write_number(row, c, pago_acumulado, money); c += 1
            sheet.write_number(row, c, saldo_restante, money); c += 1

            row += 1

        workbook.close()
        output.seek(0)
        self.write({
            'file': base64.b64encode(output.read()),
            'file_name': 'facturas_con_pagos.xlsx'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=%s&id=%s&field=file&filename=%s&download=true'
                   % (self._name, self.id, self.file_name),
            'target': 'self',
        }
