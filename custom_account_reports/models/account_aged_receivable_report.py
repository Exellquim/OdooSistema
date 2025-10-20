from odoo import models, fields, _

class AccountAgedReceivableReport(models.Model):
    _inherit = 'account.report'

    def _init_aged_receivable_with_tax(self):
        """Agregar columna 'Impuesto total' si no existe."""
        report = self.env.ref('account_reports.account_aged_receivable', raise_if_not_found=False)
        if report:
            existing = self.env['account.report.column'].search([
                ('report_id', '=', report.id),
                ('expression_label', '=', 'Impuesto total')
            ])
            if not existing:
                self.env['account.report.column'].create({
                    'report_id': report.id,
                    'name': _('Impuesto total'),
                    'expression_label': 'Impuesto total',
                    'expression': 'amount_tax_signed',
                    'figure_type': 'monetary',
                    'sortable': True,
                    'sequence': 120,
                })

    def init(self):
        """Hook que se ejecuta cuando se actualiza el módulo."""
        super().init()
        self._init_aged_receivable_with_tax()
