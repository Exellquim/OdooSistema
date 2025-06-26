from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        res = super()._create_returns()

        new_picking_id, _ = res
        return_picking = self.env['stock.picking'].browse(new_picking_id)
        
        for move in return_picking.move_ids:
            original_move = move.origin_returned_move_id
            if not original_move:
                continue

            purchase_line = original_move.purchase_line_id
            if not purchase_line:
                continue

            # Restar del qty_received
            purchase_line.qty_received -= move.product_uom_qty
            _logger.info(f"Devolución aplicada: -{move.product_uom_qty} en línea {purchase_line.id}")

            # Buscar recepciones abiertas para aumentar su cantidad
            purchase_order = purchase_line.order_id
            open_pickings = self.env['stock.picking'].search([
                ('purchase_id', '=', purchase_order.id),
                ('state', 'in', ['assigned', 'confirmed']),
                ('id', '!=', original_move.picking_id.id)
            ])

            for picking in open_pickings:
                for open_move in picking.move_ids:
                    if open_move.product_id == move.product_id:
                        open_move.product_uom_qty += move.product_uom_qty
                        _logger.info(f"Aumentando recepción {picking.name}: +{move.product_uom_qty} en producto {move.product_id.name}")
                        break

        return res
