from odoo import models, fields, api

class PickingProductSelectWizard(models.TransientModel):
    _name = 'picking.product.select.wizard'
    _description = 'Seleccionar productos del picking'

    picking_id = fields.Many2one('stock.picking', string='Albarán', required=True)
    product_ids = fields.Many2many('product.product', string='Productos')
    product_qty_ids = fields.One2many('picking.product.qty', 'wizard_id', string="Cantidades de Productos")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'default_picking_id' in self.env.context:
            picking = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
            # Obtener los productos y sus cantidades de move_ids_without_package
            product_qtys = []
            for move in picking.move_ids_without_package:
                product_qtys.append((0, 0, {
                    'product_id': move.product_id.id,
                    'product_qty': move.product_uom_qty
                }))
            res['product_qty_ids'] = product_qtys
        return res
    def action_print_selected_products(self):
        self.ensure_one()
        return self.env.ref('custom_stock_selection_report.action_report_selected_products').report_action(self)

class PickingProductQty(models.Model):
    _name = 'picking.product.qty'
    _description = 'Cantidad de producto en picking'

    wizard_id = fields.Many2one('picking.product.select.wizard', string='Wizard')
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    product_qty = fields.Float(string='Cantidad', required=True)

