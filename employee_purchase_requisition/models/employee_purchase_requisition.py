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
from odoo.exceptions import ValidationError


class PurchaseRequisition(models.Model):
    """Class for adding fields and functions for purchase requisition model."""
    _name = 'employee.purchase.requisition'
    _description = 'Solicitud de compra del empleado'
    _inherit = "mail.thread", "mail.activity.mixin"

    name = fields.Char(
        string="Número de referencia", readonly=True)
    origin = fields.Char(
        string="Origen", readonly=True)
    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Empleado',
        required=True, help='Selecciona un empleado')
    dept_id = fields.Many2one(
        comodel_name='hr.department', string='Departmento',
        related='employee_id.department_id', store=True,
        help='Selecciona un departamento')
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        required=True,
        domain=lambda self: [('share', '=', False), ('id', '!=', self.env.uid)],
        help='Seleccione un usuario que sea responsable de la requisición.')
    requisition_date = fields.Date(
        string="Fecha de requisición",
        default=lambda self: fields.Date.today(),
        help='Fecha de requisición')
    receive_date = fields.Date(
        string="Fecha de recepción", readonly=True,
        help='Fecha de recepción')
    requisition_deadline = fields.Date(
        string="Fecha límite de requisición",
        help="Fecha de finalización de la requisición de compra")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env.company,
        help='Selecciona una empresa')
    requisition_order_ids = fields.One2many(
        comodel_name='requisition.order',
        inverse_name='requisition_product_id',
        required=True)
    confirm_id = fields.Many2one(
        comodel_name='res.users',
        string='Confirmado por',
        default=lambda self: self.env.uid,
        readonly=True,
        help='El usuario que confirmó la requisición.')
    manager_id = fields.Many2one(
        comodel_name='res.users',
        string='Gerente de departamento',
        readonly=True, help='Selecciona un gerente de departamento')
    requisition_head_id = fields.Many2one(
        comodel_name='res.users',
        string='Aprobado por',
        readonly=True,
        help='Usuario que aprobó la requisición.')
    rejected_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Rechazado por',
        readonly=True,
        help='Usuario que rechazó la requisición')
    confirmed_date = fields.Date(
        string='Fecha confirmada', readonly=True,
        help='Fecha de confirmación de requisición')
    department_approval_date = fields.Date(
        string='Fecha de aprobación del departamento',
        readonly=True,
        help='Fecha de aprobación del departamento')
    approval_date = fields.Date(
        string='Fecha de aprobación', readonly=True,
        help='Fecha de aprobación de la solicitud')
    reject_date = fields.Date(
        string='Fecha de rechazo', readonly=True,
        help='Fecha de rechazo de la solicitud')
    source_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Ubicación',
        help='Ubicación de la solicitud.')
    destination_location_id = fields.Many2one(
        comodel_name='stock.location',
        string="Ubicación Destino",
        help='Ubicación de destino de la requisición.')
    delivery_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Entrega a',
        help='Tipo de entrega.')
    internal_picking_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string="Picking Interno")
    requisition_description = fields.Text(
        string="Razón de la requisición")
    purchase_count = fields.Integer(
        string='Purchase Count',
        help='Cantidad de compras',
        compute='_compute_purchase_count')
    internal_transfer_count = fields.Integer(
        string='Contador de transferencias internas',
        help='Contador de transferencias internas',
        compute='_compute_internal_transfer_count')
    state = fields.Selection(
        [('new', 'Nuevo'),
         ('waiting_department_approval', 'En espera de la aprobación del departamento'),
         ('waiting_head_approval', 'Esperando la aprobación del jefe'),
         ('approved', 'Aprobado'),
         ('purchase_order_created', 'Orden de compra creada'),
         ('received', 'Recibido'),
         ('cancelled', 'Cancelado')],
        default='new', copy=False, tracking=True)

    @api.model
    def create(self, vals):
        """Function to generate purchase requisition sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'employee.purchase.requisition') or 'New'
        result = super(PurchaseRequisition, self).create(vals)
        return result

    def action_confirm_requisition(self):
        """Function to confirm purchase requisition"""
        self.source_location_id = (
            self.employee_id.department_id.department_location_id.id) if (
            self.employee_id.department_id.department_location_id) else (
            self.env.ref('stock.stock_location_stock').id)
        self.destination_location_id = (
            self.employee_id.employee_location_id.id) if (
            self.employee_id.employee_location_id) else (
            self.env.ref('stock.stock_location_stock').id)
        self.delivery_type_id = (
            self.source_location_id.warehouse_id.in_type_id.id)
        self.internal_picking_id = (
            self.source_location_id.warehouse_id.int_type_id.id)
        self.write({'state': 'waiting_department_approval'})
        self.confirm_id = self.env.uid
        self.confirmed_date = fields.Date.today()

    def action_department_approval(self):
        """Approval from department"""
        for rec in self.requisition_order_ids:
        self.write({'state': 'waiting_head_approval'})
        self.manager_id = self.env.uid
        self.department_approval_date = fields.Date.today()

    def action_department_cancel(self):
        """Cancellation from department """
        self.write({'state': 'cancelled'})
        self.rejected_user_id = self.env.uid
        self.reject_date = fields.Date.today()

    def action_head_approval(self):
        """Approval from department head"""
        self.write({'state': 'approved'})
        self.requisition_head_id = self.env.uid
        self.approval_date = fields.Date.today()

    def action_head_cancel(self):
        """Cancellation from department head"""
        self.write({'state': 'cancelled'})
        self.rejected_user_id = self.env.uid
        self.reject_date = fields.Date.today()

    def action_create_purchase_order(self):
        """Create purchase order and internal transfer"""
        for rec in self.requisition_order_ids:
            if rec.requisition_type == 'internal_transfer':
                self.env['stock.picking'].create({
                    'location_id': self.source_location_id.id,
                    'location_dest_id': self.destination_location_id.id,
                    'picking_type_id': self.internal_picking_id.id,
                    'requisition_order': self.name,
                    'move_ids_without_package': [(0, 0, {
                        'name': rec.product_id.name,
                        'product_id': rec.product_id.id,
                        'product_uom': rec.product_id.uom_id.id,
                        'product_uom_qty': rec.quantity,
                        'location_id': self.source_location_id.id,
                        'location_dest_id': self.destination_location_id.id,
                    })]
                })
            else:
                partner = rec.partner_id or self.env.company.partner_id
                self.env['purchase.order'].create({
                    'partner_id': partner.id,
                    'requisition_order': self.name,
                    "order_line": [(0, 0, {
                        'product_id': rec.product_id.id,
                        'product_qty': rec.quantity,
                    })]})
        self.write({'state': 'purchase_order_created'})

    def _compute_internal_transfer_count(self):
        """Function to compute the transfer count"""
        self.internal_transfer_count = self.env['stock.picking'].search_count([
            ('requisition_order', '=', self.name)])

    def _compute_purchase_count(self):
        """Function to compute the purchase count"""
        self.purchase_count = self.env['purchase.order'].search_count([
            ('requisition_order', '=', self.name)])

    def action_receive(self):
        """Received purchase requisition"""
        self.write({'state': 'received'})
        self.receive_date = fields.Date.today()

    def get_purchase_order(self):
        """Purchase order smart button view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('requisition_order', '=', self.name)],
        }

    def get_internal_transfer(self):
        """Internal transfer smart tab view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Internal Transfers',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('requisition_order', '=', self.name)],
        }

    def action_print_report(self):
        """Print purchase requisition report"""
        data = {
            'employee': self.employee_id.name,
            'records': self.read(),
            'order_ids': self.requisition_order_ids.read(),
        }
        return (self.env.ref(
            'employee_purchase_requisition.'
            'action_report_purchase_requisition').report_action(
            self, data=data))
