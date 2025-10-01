from odoo import models, fields
import base64
import io
import xlsxwriter


class FacturasPagadasExcelWizard(models.TransientModel):
    _name = 'facturas.pagadas.excel.wizard'
    _description = 'Exportar reporte de facturas pagadas a Excel'

    date_start = fields.Date(string='Desde')
    date_end = fields.Date(string='Hasta')
    file = fields.Binary('Archivo Excel', readonly=True)
    file_name = fields.Char('Nombre del archivo', default='facturas_pagadas.xlsx', readonly=True)

    def exportar_excel(self):
        self.ensure_one()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Facturas Pagadas')

        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})
        datefmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        headers = [
            'Folio Factura', 'UUID', 'Cliente', 'RFC', 'País',
            'Fecha Factura', 'moneda de factura', 'total factura',
            'Subtotal conversion', 'Impuesto conversion', 'Total Factura conversion',
            'Monto Pendiente', 'Estado Pago', 'Folio Pago',
            'Fecha Pago', 'moneda pago', 'Monto Pagado', 'monto pagado conversion'
        ]
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)

        # Dominio: facturas de venta / NC, posteadas; opcionalmente por fecha de factura
        domain = [('move_type', 'in', ('out_invoice', 'out_refund')), ('state', '=', 'posted')]
        if self.date_start:
            domain.append(('invoice_date', '>=', self.date_start))
        if self.date_end:
            domain.append(('invoice_date', '<=', self.date_end))

        invoices = self.env['account.move'].search(domain, order='invoice_date,id')

        row = 1
        company = self.env.company
        mxn = self.env.ref('base.MXN')

        for inv in invoices:
            folio = inv.name or ''
            uuid = getattr(inv, 'l10n_mx_edi_cfdi_uuid', '') or ''
            if not uuid and hasattr(inv, '_get_cfdi_related_uuids'):
                uuids = inv._get_cfdi_related_uuids()
                if uuids:
                    uuid = uuids[0]

            partner = inv.partner_id
            cliente = partner.display_name or ''
            rfc = partner.vat or ''
            pais = partner.country_id.name if partner.country_id else ''
            fecha_factura = inv.invoice_date or inv.date or fields.Date.context_today(self)

            moneda_factura = inv.currency_id and inv.currency_id.name or ''
            total_factura = inv.amount_total

            # Totales convertidos a MXN con fecha de la factura
            subtotal_mxn = inv.amount_untaxed_signed
            impuesto_mxn = inv.currency_id._convert(inv.amount_tax, mxn, company, fecha_factura)
            total_mxn = inv.currency_id._convert(inv.amount_total, mxn, company, fecha_factura)

            monto_pendiente = inv.amount_residual
            estado_pago = dict(inv._fields['payment_state'].selection).get(inv.payment_state, inv.payment_state)

            # ✅ Odoo 17: filtrar por tipo de cuenta usando account_id.account_type
            receivables = inv.line_ids.filtered(
                lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')
            )
            matched_parts = (receivables.mapped('matched_debit_ids') | receivables.mapped('matched_credit_ids'))

            if not matched_parts:
                c = 0
                sheet.write(row, c, folio); c += 1
                sheet.write(row, c, uuid); c += 1
                sheet.write(row, c, cliente); c += 1
                sheet.write(row, c, rfc); c += 1
                sheet.write(row, c, pais); c += 1
                sheet.write_datetime(row, c, fields.Datetime.to_datetime(fecha_factura), datefmt); c += 1
                sheet.write(row, c, moneda_factura); c += 1
                sheet.write_number(row, c, total_factura, money); c += 1
                sheet.write_number(row, c, subtotal_mxn, money); c += 1
                sheet.write_number(row, c, impuesto_mxn, money); c += 1
                sheet.write_number(row, c, total_mxn, money); c += 1
                sheet.write_number(row, c, monto_pendiente, money); c += 1
                sheet.write(row, c, estado_pago); c += 1
                sheet.write(row, c, ''); c += 1  # Folio Pago
                sheet.write(row, c, ''); c += 1  # Fecha Pago
                sheet.write(row, c, ''); c += 1  # Moneda pago
                sheet.write(row, c, ''); c += 1  # Monto pagado
                sheet.write(row, c, ''); c += 1  # Monto pagado MXN
                row += 1
                continue

            for m in matched_parts:
                # === Identificar la línea y asiento del PAGO (no el de la factura) ===
                # Si el debit_move_id pertenece a la factura, la línea de pago será la credit_move_id; y viceversa.
                pay_ml = m.debit_move_id if m.debit_move_id.move_id.id != inv.id else m.credit_move_id
                pay_move = pay_ml.move_id
                pago = getattr(pay_move, 'payment_id', False)

                # Folio de pago: primero payment.name; si no, ref o name del asiento
                folio_pago = (pago and pago.name) or pay_move.ref or pay_move.name or ''

                # Fecha de pago: primero payment.date; si no, fecha del asiento del pago
                fecha_pago = (pago and pago.date) or pay_move.date

                # Moneda del pago: la de la línea del pago; si no hay, usa la moneda de la compañía
                pago_currency = pay_ml.currency_id or company.currency_id
                moneda_pago = pago_currency.name

                # Monto pagado en MONEDA DEL PAGO
                # No usar m.amount (está en moneda de la compañía).
                if pay_ml.id == m.credit_move_id.id:
                    amount_in_pay_cur = abs(m.credit_amount_currency or 0.0)
                else:
                    amount_in_pay_cur = abs(m.debit_amount_currency or 0.0)

                if not pay_ml.currency_id or pay_ml.currency_id == company.currency_id:
                    # La línea está en moneda de la compañía => usar m.amount
                    monto_pagado = abs(m.amount or 0.0)
                else:
                    # Usar el amount_currency específico en la línea del pago
                    monto_pagado = amount_in_pay_cur

                # Conversión a MXN (o a la que necesites) con FECHA DE PAGO
                monto_pagado_mxn = pago_currency._convert(monto_pagado, mxn, company, fecha_pago or fecha_factura)

                # --- Escribir fila ---
                c = 0
                sheet.write(row, c, folio); c += 1
                sheet.write(row, c, uuid); c += 1
                sheet.write(row, c, cliente); c += 1
                sheet.write(row, c, rfc); c += 1
                sheet.write(row, c, pais); c += 1
                sheet.write_datetime(row, c, fields.Datetime.to_datetime(fecha_factura), datefmt); c += 1
                sheet.write(row, c, moneda_factura); c += 1
                sheet.write_number(row, c, total_factura, money); c += 1
                sheet.write_number(row, c, subtotal_mxn, money); c += 1
                sheet.write_number(row, c, impuesto_mxn, money); c += 1
                sheet.write_number(row, c, total_mxn, money); c += 1
                sheet.write_number(row, c, monto_pendiente, money); c += 1
                sheet.write(row, c, estado_pago); c += 1
                sheet.write(row, c, folio_pago); c += 1
                if fecha_pago:
                    sheet.write_datetime(row, c, fields.Datetime.to_datetime(fecha_pago), datefmt)
                else:
                    sheet.write(row, c, '')
                c += 1
                sheet.write(row, c, moneda_pago); c += 1
                sheet.write_number(row, c, monto_pagado, money); c += 1          # Monto en moneda del pago
                sheet.write_number(row, c, monto_pagado_mxn, money); c += 1     # Conversión a MXN
                row += 1

        # Fila de totales
        total_row = row + 1
        sheet.write(total_row, 0, "TOTALES", bold)

        # Columnas numéricas que se suman
        numeric_cols = [7, 8, 9, 10, 11, 16, 17]
        for col in numeric_cols:
            col_letter = chr(ord('A') + col)  # A=0, B=1, ...
            formula = f"=SUM({col_letter}2:{col_letter}{row})"
            sheet.write_formula(total_row, col, formula, money)

        workbook.close()
        output.seek(0)
        data = output.read()
        self.write({
            'file': base64.b64encode(data),
            'file_name': 'facturas_pagadas.xlsx',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=%s&id=%s&field=file&filename=%s&download=true'
                   % (self._name, self.id, self.file_name),
            'target': 'self',
        }
