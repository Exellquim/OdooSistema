from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_open_product_select_wizard(self):
        return {
            'name': 'Seleccionar productos',
            'type': 'ir.actions.act_window',
            'res_model': 'picking.product.select.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_picking_id': self.id},
        }
    def button_actualizar(self):
        for move in self.move_ids_without_package:
            move.quantity = 0.0  # Este es el campo correcto para modificar la cantidad realizada
        return True

class StockMove(models.Model):
    _inherit = 'stock.move'

    camas_x_pallet = fields.Float(string="Camas por Pallet", help="Número de camas por pallet")
    cajas_x_pallet = fields.Float(string="Cajas por Pallet", help="Número de cajas por pallet")
    unidades_sku_x_pallet = fields.Float(string="Unidades SKU por Pallet", help="Número de unidades SKU por pallet")


