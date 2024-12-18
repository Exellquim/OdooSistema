from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    qty_invoiced = fields.Float(
        string='Cantidad Facturada',
        related='order_line.qty_invoiced',
        readonly=False
    )