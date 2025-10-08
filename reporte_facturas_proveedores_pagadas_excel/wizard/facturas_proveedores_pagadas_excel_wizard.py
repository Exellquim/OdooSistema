from odoo import models, fields, api, _
import base64
import io
import json
import xlsxwriter

class FacturasProveedoresPagadasExcelWizard(models.TransientModel):
    _name = 'facturas.proveedores.pagadas.excel.wizard'
    _description = 'Exportar reporte de facturas de proveedores pagadas a Excel'

    date_start = fields.Date(string='Desde')
    date_end = fields.Date(string='Hasta')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    file = fields.Binary('Archivo Excel', readonly=True)
    file_name = fields.Char('Nombre del archivo', default='facturas_proveedores_pagadas.xlsx', readonly=True)

    def _payment_items_from_invoice(self, inv):
        """Regresa una lista de líneas de pago a partir del widget de pagos."""
        items = []
        widget = inv.invoice_payments_widget
        if not widget:
            return items
        try:
            data = widget if isinstance(widget, dict) else json.loads(widget)
            for line in data.get('content', []):
                items.append(line)
        except Exception:
            pass
        return items

    def _is_in_range(self, dt):
        """Valida si una fecha (string o date) está dentro del rango seleccionado."""
        if not dt:
            return False
        try:
            dt_date = fields.Date.from_string(dt) if isinstance(dt, str) else dt
        except Exception:
            try:
                dt_date = fields.Datetime.to_datetime(dt).date()
            except Exception:
                return False
        start = self.date_start or fields.Date.from_string('1900-01-01')
        end = self.date_end or fields.Date.from_string('2999-12-31')
        return start <= dt_date <= end

    def _iter_vendor_invoice_payment_rows(self):
        """Itera facturas de proveedor pagadas y produce dicts fila por pago."""
        domain = [
            ('move_type', 'in', ['in_invoice', 'in_refund']),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('company_id', '=', self.company_id.id),
        ]
        invoices = self.env['account.move'].search(domain, order='invoice_date, name')
        Currency = self.env['res.currency']

        for inv in invoices:
            currency = inv.currency_id
            for pay in self._payment_items_from_invoice(inv):
                pay_date = pay.get('date')
                if not self._is_in_range(pay_date):
                    continue

                currency_code = currency.name
                currency_id = pay.get('currency_id')
                if currency_id and isinstance(currency_id, int):
                    cur = Currency.browse(currency_id)
                    if cur.exists():
                        currency_code = cur.name

                yield {
                    'partner': inv.partner_id.name or '',
                    'invoice': inv.name or inv.ref or '',
                    'invoice_date': inv.invoice_date,
                    'invoice_due': inv.invoice_date_due or inv.invoice_date,
                    'invoice_total': inv.amount_total,
                    'currency_code': currency_code,
                    'payment_date': pay.get('date'),
                    'payment_ref': pay.get('name') or '',
                    'payment_journal': pay.get('journal_name') or '',
                    'paid_amount': pay.get('amount') or 0.0,
                    'company': inv.company_id.display_name,
                }

    def exportar_excel(self):
        self.ensure_one()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(_('Pagos de Proveedores'))

        title = workbook.add_format({'bold': True, 'font_size': 14})
        header = workbook.add_format({'bold': True, 'bg_color': '#DDDDDD', 'border': 1})
        cell = workbook.add_format({'border': 1})
        date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00', 'border': 1})

        sheet.merge_range(0, 0, 0, 10, _('Facturas de Proveedores Pagadas'), title)

        columns = [
            _('Proveedor'),
            _('Factura'),
            _('Fecha Factura'),
            _('Vencimiento'),
            _('Moneda'),
            _('Total Factura'),
            _('Fecha Pago'),
            _('Diario de Pago'),
            _('Referencia de Pago'),
            _('Monto Pagado'),
            _('Compañía'),
        ]
        for c, name in enumerate(columns):
            sheet.write(2, c, name, header)
            sheet.set_column(c, c, 18)

        
        row = 3
        total_paid = 0.0
        for line in self._iter_vendor_invoice_payment_rows():
            # Fechas de factura
            if line['invoice_date']:
                sheet.write_datetime(row, 2, fields.Datetime.to_datetime(line['invoice_date']), date_fmt)
            else:
                sheet.write(row, 2, '', cell)

            if line['invoice_due']:
                sheet.write_datetime(row, 3, fields.Datetime.to_datetime(line['invoice_due']), date_fmt)
            else:
                sheet.write(row, 3, '', cell)

            # Fecha de pago desde widget (string)
            dt = None
            try:
                d = fields.Date.from_string(line['payment_date']) if isinstance(line['payment_date'], str) else line['payment_date']
                dt = fields.Datetime.to_datetime(d) if d else None
            except Exception:
                dt = None

            sheet.write(row, 0, line['partner'], cell)
            sheet.write(row, 1, line['invoice'], cell)
            sheet.write(row, 4, line['currency_code'], cell)
            sheet.write_number(row, 5, line['invoice_total'] or 0.0, money)
            sheet.write_datetime(row, 6, dt, date_fmt) if dt else sheet.write(row, 6, line['payment_date'] or '', cell)
            sheet.write(row, 7, line['payment_journal'], cell)
            sheet.write(row, 8, line['payment_ref'], cell)
            sheet.write_number(row, 9, line['paid_amount'] or 0.0, money)
            sheet.write(row, 10, line['company'], cell)

            total_paid += line['paid_amount'] or 0.0
            row += 1

        # Totales
        sheet.write(row, 8, _('Total pagado:'), header)
        sheet.write_number(row, 9, total_paid, money)

        workbook.close()
        output.seek(0)
        data = output.read()

        self.write({
            'file': base64.b64encode(data),
            'file_name': 'facturas_proveedores_pagadas.xlsx',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=%s&id=%s&field=file&filename=%s&download=true'
                   % (self._name, self.id, self.file_name),
            'target': 'self',
        }
