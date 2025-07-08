# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Ashok PK (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models


class RequisitionProducts(models.Model):
    _name = 'requisition.order'
    _description = 'Órden de Compra'

    requisition_product_id = fields.Many2one(
        comodel_name='employee.purchase.requisition',
        help='Requisitar producto.')
    state = fields.Selection(
        string='Estado',
        related='requisition_product_id.state')
    requisition_type = fields.Selection(
        string='Tipo de requisición',
        selection=[('purchase_order', 'Órden de Compra'),
                   ('internal_transfer', 'Transferencia Interna'), ],
        help='Tipo de requisición', required=True, default='purchase_order')
    product_id = fields.Many2one(
        comodel_name='product.product', required=True,
        help='Producto')
    description = fields.Text(
        string="Descripción",
        compute='_compute_name',
        store=True, readonly=False,
        precompute=True, help='Descripción del Producto')
    quantity = fields.Integer(
        string='Cantidad', help='Cantidad del producto')
    uom = fields.Char(
        related='product_id.uom_id.name',
        string='Unidad de Medida', help='Unidad de medida del producto')
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Proveedor',
        help='Proveedor para la requisición',readonly=False)
    approved_line = fields.Boolean(
        string='Aprobado', help='Indica si la línea fue aprobada')

    approved_quantity = fields.Integer(
        string='Cantidad Aprobada', help='Cantidad autorizada para compra o transferencia')

    @api.depends('product_id')
    def _compute_name(self):
        """Compute product description"""
        for option in self:
            if not option.product_id:
                continue
            product_lang = option.product_id.with_context(
                lang=self.requisition_product_id.employee_id.lang)
            option.description = product_lang.get_product_multiline_description_sale()

    @api.onchange('requisition_type')
    def _onchange_product(self):
        """Fetching product vendors"""
        vendors_list = [data.partner_id.id for data in
                        self.product_id.seller_ids]
        return {'domain': {'partner_id': [('id', 'in', vendors_list)]}}
