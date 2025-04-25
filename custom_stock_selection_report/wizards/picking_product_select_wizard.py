from odoo import models, fields, api

class PickingProductSelectWizard(models.TransientModel):
    _name = 'picking.product.select.wizard'
    _description = 'Seleccionar productos del picking'

    picking_id = fields.Many2one('stock.picking', string='Albarán', required=True)
    product_ids = fields.Many2many('product.product', string='Productos')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'default_picking_id' in self.env.context:
            picking = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
            res['product_ids'] = [(6, 0, picking.move_ids_without_package.mapped('product_id').ids)]
        return res

    def action_print_selected_products(self):
        self.ensure_one()

        selected_products = []
        for product in self.product_ids:
            selected_products.append({
                'name': product.display_name,
            })

        data = {
            'products': selected_products,
            'picking_name': self.picking_id.name,
        }

        return self.env.ref('custom_stock_selection_report.action_report_selected_products').report_action(self, data=data)


