# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    reconcile_invoice_ids = fields.One2many('account.payment.reconcile', 'payment_id', string="Invoices", copy=False)

    def open_invoice_selection_wizard(self):
        return {
            'name': 'Select Invoices for Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
            },
        }

    @api.onchange('reconcile_invoice_ids')
    def _onchnage_reconcile_invoice_ids(self):
        payment_amount = 0.0
        for line in self.reconcile_invoice_ids.filtered(lambda x: x.amount_paid > 0):
            if self.currency_id != line.currency_id:
                payment_amount += line.currency_id._convert(line.amount_paid, self.currency_id, self.env.company, self.date)
            else:
                payment_amount += line.amount_paid
        self.amount = payment_amount


    def action_post(self, *args, **kwargs):
        # Llamar a la implementación original de action_post
        res = super(AccountPayment, self).action_post(*args, **kwargs)

        # Obtener las líneas de movimientos contables
        move_lines = self.env['account.move.line']
        
        # Filtrar las líneas de reconciliación con monto pagado
        rec_lines = self.reconcile_invoice_ids.filtered(lambda x: x.amount_paid > 0)
        
        if rec_lines:
            for line in rec_lines:
                # Filtrar las líneas de la factura y del pago para cuentas por cobrar/pagar (usando 'account_type')
                invoice_move = line.invoice_id.line_ids.filtered(
                    lambda r: not r.reconciled and r.account_id.account_type in ('asset_receivable', 'liability_payable')
                )
                payment_move = line.payment_id.move_id.line_ids.filtered(
                    lambda r: not r.reconciled and r.account_id.account_type in ('asset_receivable', 'liability_payable')
                )

                # Añadir las líneas de movimiento a la colección
                move_lines |= (invoice_move + payment_move)

                # Crear reconciliación parcial dependiendo del tipo de partner
                if invoice_move and payment_move and len(rec_lines) > 0:
                    if self.partner_type == 'customer':
                        rec = self.env['account.partial.reconcile'].create({
                            'amount': abs(line.amount_paid),
                            'debit_amount_currency': abs(line.amount_paid),
                            'credit_amount_currency': abs(line.amount_paid),
                            'debit_move_id': invoice_move.id,
                            'credit_move_id': payment_move.id,
                        })
                    else:
                        rec = self.env['account.partial.reconcile'].create({
                            'amount': abs(line.amount_paid),
                            'debit_amount_currency': abs(line.amount_paid),
                            'credit_amount_currency': abs(line.amount_paid),
                            'debit_move_id': payment_move.id,
                            'credit_move_id': invoice_move.id,
                        })
            
            # Reconciliar las líneas de movimientos no reconciliadas
            move_lines.filtered(lambda x: not x.reconciled).reconcile()

        return res
        
class AccountPaymentInvoiceWizard(models.TransientModel):
    _name = 'account.payment.invoice.wizard'
    _description = 'Wizard for selecting invoices for payment reconciliation'

    payment_id = fields.Many2one('account.payment', string="Payment")
    invoice_ids = fields.Many2many(
        'account.move', string="Invoices",
        domain="[('partner_id', '=', partner_id), ('state', '=', 'posted'), ('payment_state', 'not in', ['paid', 'reversed', 'in_payment'])]"
    )
    partner_id = fields.Many2one('res.partner', related='payment_id.partner_id', string="Partner", readonly=True)
    payment_type = fields.Selection(related='payment_id.payment_type', readonly=True)

class AccountPaymentInvoiceWizard(models.TransientModel):
    _name = 'account.payment.invoice.wizard'
    _description = 'Wizard for selecting invoices for payment reconciliation'

    payment_id = fields.Many2one('account.payment', string="Payment")
    invoice_ids = fields.Many2many(
    'account.move', string="Invoices",
    domain="[('partner_id', '=', partner_id), ('state', '=', 'posted'), "
            "('payment_state', 'not in', ['paid', 'reversed', 'in_payment']), "
            "('move_type', 'in', ['out_invoice', 'in_invoice'])]"
    )

    partner_id = fields.Many2one('res.partner', related='payment_id.partner_id', string="Partner", readonly=True)
    payment_type = fields.Selection(related='payment_id.payment_type', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(AccountPaymentInvoiceWizard, self).default_get(fields)
        payment_id = self.env.context.get('active_id')
        if payment_id:
            payment = self.env['account.payment'].browse(payment_id)
            res.update({
                'payment_id': payment_id,
            })
        return res

    def action_add_invoices(self):
        # Solo las facturas seleccionadas en el campo invoice_ids serán procesadas y guardadas.
        reconcile_lines = []
        for invoice in self.invoice_ids:
            already_paid = sum(invoice.line_ids.mapped('matched_debit_ids.amount')) + sum(invoice.line_ids.mapped('matched_credit_ids.amount'))
            reconcile_lines.append((0, 0, {
                'payment_id': self.payment_id.id,
                'invoice_id': invoice.id,
                'already_paid': already_paid,
                'amount_residual': invoice.amount_residual,
                'amount_untaxed': invoice.amount_untaxed,
                'amount_tax': invoice.amount_tax,
                'currency_id': invoice.currency_id.id,
                'amount_total': invoice.amount_total,
            }))
        
        # Guardamos solo las líneas de reconciliación de las facturas seleccionadas en el campo reconcile_invoice_ids
        self.payment_id.reconcile_invoice_ids = reconcile_lines
        return {'type': 'ir.actions.act_window_close'}


class AccountPaymentReconcile(models.Model):
    _name = 'account.payment.reconcile'

    def _check_full_deduction(self):
        if self.invoice_id:
            payment_ids = [payment['account_payment_id'] for payment in
                           self.invoice_id._get_reconciled_info_JSON()]
            if payment_ids:
                payments = self.env['account.payment'].browse(payment_ids)
                return any([True if payment.tds_amt or payment.sales_tds_amt else False for payment in payments])
            else:
                return False

    payment_id = fields.Many2one('account.payment')
    reconcile = fields.Boolean(string="Select")
    invoice_id = fields.Many2one('account.move', required=True)
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', readonly=True)
    amount_total = fields.Monetary(string='Total')
    amount_untaxed = fields.Monetary(string='Untaxed Amount')
    amount_tax = fields.Monetary(string='Taxes Amount')
    already_paid = fields.Monetary("Amount Paid")
    amount_residual = fields.Monetary('Amount Due')
    amount_paid = fields.Monetary(string="Payment Amount")

    @api.onchange('amount_paid')
    def _onchange_amount_paid(self):
        if self.amount_paid > self.amount_residual:
            raise ValidationError(_('You cannot pay more than residual amount.'))

    def pw_action_post_custom(self):
        for payment in self:
            if ((payment.sales_tds_type in ['excluding',
                                            'including'] and payment.sales_tds_tax_id and payment.sales_tds_amt and payment.bill_type == 'non_bill') and not payment.tds_tax_id):
                if payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                    sales_tds_amt = payment.amount - payment.sales_tds_amt
                    sales_tax_repartition_lines = payment.sales_tds_tax_id.invoice_repartition_line_ids.filtered(
                        lambda x: x.repartition_type == 'tax')
                    if payment.sales_tds_type == "excluding":
                        sales_excld_amt = payment.amount + payment.sales_tds_amt
                        payment.move_id.button_draft()
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': sales_excld_amt,
                                     'debit': sales_excld_amt,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'currency_id': currency,
                                     'account_id': debitacc,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': payment.amount,
                                     'debit': 0,
                                     'credit': payment.amount,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Sale Tax Withhold'),
                                     'amount_currency': payment.sales_tds_amt,
                                     'debit': 0,
                                     'credit': payment.sales_tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': sales_tax_repartition_lines.id and sales_tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()
                    if payment.sales_tds_type == "including":
                        payment.move_id.button_draft()
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': payment.amount,
                                     'debit': payment.amount,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': debitacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': sales_tds_amt,
                                     'debit': 0,
                                     'credit': sales_tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Sale Tax Withhold'),
                                     'amount_currency': payment.sales_tds_amt,
                                     'debit': 0,
                                     'credit': payment.sales_tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': sales_tax_repartition_lines.id and sales_tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()

            if ((payment.tds_type in ['excluding',
                                      'including'] and payment.tds_tax_id and payment.tds_amt and payment.bill_type == 'non_bill') and not payment.sales_tds_tax_id):
                if payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                    tds_amt = payment.amount - payment.tds_amt
                    tax_repartition_lines = payment.tds_tax_id.invoice_repartition_line_ids.filtered(
                        lambda x: x.repartition_type == 'tax')
                    if payment.tds_type == "excluding":
                        excld_amt = payment.amount + payment.tds_amt
                        payment.move_id.button_draft()
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': excld_amt,
                                     'debit': excld_amt,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'currency_id': currency,
                                     'account_id': debitacc,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': payment.amount,
                                     'debit': 0,
                                     'credit': payment.amount,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': payment.currency_id.id,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Income Tax Withhold'),
                                     'amount_currency': payment.tds_amt,
                                     'debit': 0,
                                     'credit': payment.tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()
                    if payment.tds_type == "including":
                        payment.move_id.button_draft()
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': payment.amount,
                                     'debit': payment.amount,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': debitacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': tds_amt,
                                     'debit': 0,
                                     'credit': tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Income Tax Withhold'),
                                     'amount_currency': payment.tds_amt,
                                     'debit': 0,
                                     'credit': payment.tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()
            if ((payment.tds_type in ['excluding', 'including'] and payment.sales_tds_type in ['excluding',
                                                                                               'including'] and payment.tds_tax_id and payment.tds_amt and payment.sales_tds_tax_id and payment.sales_tds_amt and payment.bill_type == 'non_bill')):
                if payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                    if payment.tds_type == 'including' or payment.sales_tds_type == 'including':

                        payment.move_id.button_draft()
                        tax_repartition_lines = payment.tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        sales_tax_repartition_lines = payment.sales_tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        payamt = payment.amount
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        tds_amt_inc = payment.amount - (payment.tds_amt + payment.sales_tds_amt)
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': payment.amount,
                                     'debit': payment.amount,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': debitacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': tds_amt_inc,
                                     'debit': 0,
                                     'credit': tds_amt_inc,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Income Tax Withhold'),
                                     'amount_currency': payment.tds_amt,
                                     'debit': 0,
                                     'credit': payment.tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Sale Tax Withhold'),
                                     'amount_currency': payment.sales_tds_amt,
                                     'debit': 0,
                                     'credit': payment.sales_tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': sales_tax_repartition_lines.id and sales_tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()

            if ((payment.tds_type in ['excluding'] and payment.sales_tds_type in [
                'excluding'] and payment.tds_tax_id and payment.tds_amt and payment.sales_tds_tax_id and payment.sales_tds_amt and payment.bill_type == 'non_bill')):
                if payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                    if payment.tds_type == 'excluding' and payment.sales_tds_type == 'excluding':

                        payment.move_id.button_draft()
                        tax_repartition_lines = payment.tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        sales_tax_repartition_lines = payment.sales_tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        payamt = payment.amount
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        tds_amt_inc = payment.amount - (payment.tds_amt + payment.sales_tds_amt)
                        vals = []
                        excluding_debit = payment.amount + payment.tds_amt + payment.sales_tds_amt
                        vals.append({'name': debitref,
                                     'amount_currency': payment.amount,
                                     'debit': excluding_debit,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': debitacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': tds_amt_inc,
                                     'debit': 0,
                                     'credit': payment.amount,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Income Tax Withhold'),
                                     'amount_currency': payment.tds_amt,
                                     'debit': 0,
                                     'credit': payment.tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Sale Tax Withhold'),
                                     'amount_currency': payment.sales_tds_amt,
                                     'debit': 0,
                                     'credit': payment.sales_tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': sales_tax_repartition_lines.id and sales_tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()
            # payment.amount = payamt

            # Bill Type = Bill
            if ((payment.sales_tds_type in ['excluding',
                                            'including'] and payment.sales_tds_tax_id and payment.sales_tds_amt and payment.bill_type == 'bill') and not payment.tds_tax_id):
                if payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                    sales_tds_amt = payment.amount - payment.sales_tds_amt
                    sales_tax_repartition_lines = payment.sales_tds_tax_id.invoice_repartition_line_ids.filtered(
                        lambda x: x.repartition_type == 'tax')
                    if payment.sales_tds_type == "excluding":
                        sales_excld_amt = payment.amount + payment.sales_tds_amt
                        payment.move_id.button_draft()
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': sales_excld_amt,
                                     'debit': sales_excld_amt,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'currency_id': currency,
                                     'account_id': debitacc,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': payment.amount,
                                     'debit': 0,
                                     'credit': payment.amount,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Sale Tax Withhold'),
                                     'amount_currency': payment.sales_tds_amt,
                                     'debit': 0,
                                     'credit': payment.sales_tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': sales_tax_repartition_lines.id and sales_tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()
                    if payment.sales_tds_type == "including":
                        payment.move_id.button_draft()
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': payment.amount,
                                     'debit': payment.amount,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': debitacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': sales_tds_amt,
                                     'debit': 0,
                                     'credit': sales_tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Sale Tax Withhold'),
                                     'amount_currency': payment.sales_tds_amt,
                                     'debit': 0,
                                     'credit': payment.sales_tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': sales_tax_repartition_lines.id and sales_tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()

            if ((payment.tds_type in ['excluding',
                                      'including'] and payment.tds_tax_id and payment.tds_amt and payment.bill_type == 'bill') and not payment.sales_tds_tax_id):
                if payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                    tds_amt = payment.amount - payment.tds_amt
                    tax_repartition_lines = payment.tds_tax_id.invoice_repartition_line_ids.filtered(
                        lambda x: x.repartition_type == 'tax')
                    if payment.tds_type == "excluding":
                        excld_amt = payment.amount + payment.tds_amt
                        payment.move_id.button_draft()
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': excld_amt,
                                     'debit': excld_amt,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'currency_id': currency,
                                     'account_id': debitacc,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': payment.amount,
                                     'debit': 0,
                                     'credit': payment.amount,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Income Tax Withhold'),
                                     'amount_currency': payment.tds_amt,
                                     'debit': 0,
                                     'credit': payment.tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()
                    if payment.tds_type == "including":
                        payment.move_id.button_draft()
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': payment.amount,
                                     'debit': payment.amount,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': debitacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': tds_amt,
                                     'debit': 0,
                                     'credit': tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Income Tax Withhold'),
                                     'amount_currency': payment.tds_amt,
                                     'debit': 0,
                                     'credit': payment.tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'payment_id': payment.id,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()
            if (payment.tds_type in ['excluding', 'including'] and payment.sales_tds_type in ['excluding',
                                                                                              'including'] and payment.tds_tax_id and payment.tds_amt and payment.sales_tds_tax_id and payment.sales_tds_amt and payment.bill_type == 'bill') or payment.income_account_id and payment.sales_account_id:
                if payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                    if payment.tds_type == 'including' or payment.sales_tds_type == 'including' or payment.wht_type == 'amount':
                        payment.move_id.button_draft()
                        tax_repartition_lines = payment.tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        sales_tax_repartition_lines = payment.sales_tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        payamt = payment.amount
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        tds_amt_inc = payment.amount - (payment.tds_amt + payment.sales_tds_amt)
                        vals = []
                        vals.append({'name': debitref,
                                     'amount_currency': payment.amount,
                                     'debit': payment.amount,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': debitacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': tds_amt_inc,
                                     'debit': 0,
                                     'credit': tds_amt_inc,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        if payment.tds_amt:
                            vals.append({'name': _('Income Tax Withhold'),
                                         'amount_currency': payment.tds_amt,
                                         'debit': 0,
                                         'credit': payment.tds_amt,
                                         'date_maturity': payment.date,
                                         'partner_id': payment.partner_id.id,
                                         'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id or payment.income_account_id.id,
                                         'currency_id': currency,
                                         # 'move_id': payment.move_id.id
                                         })
                        if payment.sales_tds_amt:
                            vals.append({'name': _('Sale Tax Withhold'),
                                         'amount_currency': payment.sales_tds_amt,
                                         'debit': 0,
                                         'credit': payment.sales_tds_amt,
                                         'date_maturity': payment.date,
                                         'partner_id': payment.partner_id.id,
                                         'account_id': sales_tax_repartition_lines.id and sales_tax_repartition_lines.account_id.id or payment.sales_account_id.id,
                                         'currency_id': currency,
                                         # 'move_id': payment.move_id.id
                                         })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()

            if ((payment.tds_type in ['excluding'] and payment.sales_tds_type in [
                'excluding'] and payment.tds_tax_id and payment.tds_amt and payment.sales_tds_tax_id and payment.sales_tds_amt and payment.bill_type == 'bill')):
                if payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                    if payment.tds_type == 'excluding' and payment.sales_tds_type == 'excluding':

                        payment.move_id.button_draft()
                        tax_repartition_lines = payment.tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        sales_tax_repartition_lines = payment.sales_tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        payamt = payment.amount
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        tds_amt_inc = payment.amount - (payment.tds_amt + payment.sales_tds_amt)
                        vals = []
                        excluding_debit = payment.amount + payment.tds_amt + payment.sales_tds_amt
                        vals.append({'name': debitref,
                                     'amount_currency': payment.amount,
                                     'debit': excluding_debit,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': debitacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': creditref,
                                     'amount_currency': tds_amt_inc,
                                     'debit': 0,
                                     'credit': payment.amount,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Income Tax Withhold'),
                                     'amount_currency': payment.tds_amt,
                                     'debit': 0,
                                     'credit': payment.tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': _('Sale Tax Withhold'),
                                     'amount_currency': payment.sales_tds_amt,
                                     'debit': 0,
                                     'credit': payment.sales_tds_amt,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': sales_tax_repartition_lines.id and sales_tax_repartition_lines.account_id.id,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()

            if payment.tds_type in ['excluding', 'including'] or payment.sales_tds_type in ['excluding',
                                                                                            'including'] and (
                    payment.tds_tax_id and payment.tds_amt) or (
                    payment.sales_tds_tax_id and payment.sales_tds_amt) and payment.bill_type == 'bill' or payment.income_account_id or payment.sales_account_id:
                if payment.payment_type == 'inbound' and payment.partner_type == 'customer':
                    if payment.tds_type == 'including' or payment.sales_tds_type == 'including' or payment.wht_type == 'amount':
                        payment.move_id.button_draft()
                        tax_repartition_lines = payment.tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        sales_tax_repartition_lines = payment.sales_tds_tax_id.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        creditacc = 0
                        debitacc = 0
                        creditref = 0
                        debitref = 0
                        currency = payment.move_id.currency_id.id
                        payamt = payment.amount
                        for rec in payment.move_id.line_ids:
                            if rec.debit == 0:
                                creditacc = rec.account_id.id
                                creditref = rec.name
                            if rec.credit == 0:
                                debitacc = rec.account_id.id
                                debitref = rec.name
                        payment.move_id.line_ids.unlink()
                        tds_amt_inc = payment.amount - (payment.tds_amt + payment.sales_tds_amt)
                        vals = []
                        vals.append({'name': creditref,
                                     'amount_currency': payment.amount,
                                     'debit': 0,
                                     'credit': payment.amount,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': creditacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        vals.append({'name': debitref,
                                     'amount_currency': tds_amt_inc,
                                     'debit': tds_amt_inc,
                                     'credit': 0,
                                     'date_maturity': payment.date,
                                     'partner_id': payment.partner_id.id,
                                     'account_id': debitacc,
                                     'currency_id': currency,
                                     # 'move_id': payment.move_id.id
                                     })
                        if payment.tds_amt:
                            vals.append({'name': _('Income Tax Withhold'),
                                         'amount_currency': payment.tds_amt,
                                         'debit': payment.tds_amt,
                                         'credit': 0,
                                         'date_maturity': payment.date,
                                         'partner_id': payment.partner_id.id,
                                         'account_id': tax_repartition_lines.id and tax_repartition_lines.account_id.id or payment.income_account_id.id,
                                         'currency_id': currency,
                                         # 'move_id': payment.move_id.id
                                         })
                        if payment.sales_tds_amt:
                            vals.append({'name': _('Sale Tax Withhold'),
                                         'amount_currency': payment.sales_tds_amt,
                                         'debit': payment.sales_tds_amt,
                                         'credit': 0,
                                         'date_maturity': payment.date,
                                         'partner_id': payment.partner_id.id,
                                         'account_id': sales_tax_repartition_lines.id and sales_tax_repartition_lines.account_id.id or payment.sales_account_id.id,
                                         'currency_id': currency,
                                         # 'move_id': payment.move_id.id
                                         })
                        lines = [(0, 0, line_move) for line_move in vals]
                        payment.move_id.write({'line_ids': lines})
                        payment.move_id.write({'currency_id': currency})
                        payment.move_id.action_post()

        return res
