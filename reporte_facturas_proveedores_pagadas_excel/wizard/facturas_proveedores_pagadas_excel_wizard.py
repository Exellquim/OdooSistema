from odoo import models, fields
import base64
import io
import xlsxwriter


class FacturasProveedoresExcelWizard(models.TransientModel):
    _name = 'facturas.proveedores.pagadas.excel.wizard'
    _description = 'Exportar reporte de facturas de proveedores pagadas a Excel'

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
        readonly=True
    )

    date_start = fields.Date(string='Desde')
    date_end = fields.Date(string='Hasta')
    file = fields.Binary('Archivo Excel', readonly=True)
    file_name = fields.Char('Nombre del archivo', default='facturas_proveedores.xlsx', readonly=True)

    def exportar_excel(self):
        self.ensure_one()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Facturas Proveedores')

        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})
        datefmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        headers = [
            'Folio Factura', 'UUID', 'Proveedor', 'RFC', 'País',
            'Fecha Factura', 'Moneda Factura', 'Total Factura',
            'Subtotal Conversion', 'Impuesto Conversion', 'Total Factura Conversion',
            'Monto Pendiente', 'Estado Pago', 'Folio Pago',
            'Fecha Pago', 'Moneda Pago', 'Monto Pagado', 'Monto Pagado Conversion'
        ]
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)

        # Facturas de proveedores
        domain = [('move_type', 'in', ('in_invoice', 'in_refund')), ('state', '=', 'posted')]
        if self.date_start:
            domain.append(('invoice_date', '>=', self.date_start))
        if self.date_end:
            domain.append(('invoice_date', '<=', self.date_end))

        invoices = self.env['account.move'].search(domain, order='invoice_date,id')

        row = 1

        for inv in invoices:
            folio = inv.name or ''
            uuid = getattr(inv, 'l10n_mx_edi_cfdi_uuid', '') or ''
            partner = inv.partner_id
            proveedor = partner.display_name or ''
            rfc = partner.vat or ''
            pais = partner.country_id.name if partner.country_id else ''
            fecha_factura = inv.invoice_date or inv.date or fields.Date.context_today(self)
            moneda_factura = inv.currency_id.name or ''
            total_factura = inv.amount_total
            subtotal_mxn = inv.amount_untaxed_signed
            impuesto_mxn = inv.amount_tax_signed
            total_mxn = inv.amount_total_signed
            monto_pendiente = inv.amount_residual
            estado_pago = dict(inv._fields['payment_state'].selection).get(inv.payment_state, inv.payment_state)

            # Pagos relacionados (Odoo trae esta función lista)
            pagos = inv._get_reconciled_info_JSON_values()

            if pagos:
                for pago in pagos:
                    c = 0
                    sheet.write(row, c, folio); c += 1
                    sheet.write(row, c, uuid); c += 1
                    sheet.write(row, c, proveedor); c += 1
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

                    # Datos del pago
                    sheet.write(row, c, pago.get('move_name', '')); c += 1
                    fecha_pago = pago.get('date')
                    if fecha_pago:
                        sheet.write_datetime(row, c, fields.Datetime.to_datetime(fecha_pago), datefmt)
                    else:
                        sheet.write(row, c, '')
                    c += 1
                    sheet.write(row, c, pago.get('currency', '')); c += 1
                    sheet.write_number(row, c, pago.get('amount', 0.0), money); c += 1
                    sheet.write_number(row, c, pago.get('amount_company_currency', 0.0), money); c += 1
                    row += 1
            else:
                # Si no tiene pagos, igual escribimos la fila vacía
                c = 0
                sheet.write(row, c, folio); c += 1
                sheet.write(row, c, uuid); c += 1
                sheet.write(row, c, proveedor); c += 1
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
                sheet.write(row, c, ''); c += 1
                sheet.write(row, c, ''); c += 1
                sheet.write(row, c, ''); c += 1
                sheet.write(row, c, ''); c += 1
                sheet.write(row, c, ''); c += 1
                row += 1

        workbook.close()
        output.seek(0)
        data = output.read()
        self.write({
            'file': base64.b64encode(data),
            'file_name': 'facturas_proveedores.xlsx',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=%s&id=%s&field=file&filename=%s&download=true'
                   % (self._name, self.id, self.file_name),
            'target': 'self',
        }
