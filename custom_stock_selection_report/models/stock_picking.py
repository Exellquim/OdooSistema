from odoo import models

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
