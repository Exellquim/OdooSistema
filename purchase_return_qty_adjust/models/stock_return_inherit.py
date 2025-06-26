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

            # 1. Restar del qty_received
            purchase_line.qty_received -= move.product_uom_qty
            _logger.info(f"Devolución aplicada: -{move.product_uom_qty} en línea {purchase_line.id}")

            # 2. Si no hay recepciones abiertas, forzar nueva creando por aumento temporal
            purchase_order = purchase_line.order_id
            pickings = self.env['stock.picking'].search([
                ('purchase_id', '=', purchase_order.id),
                ('state', 'in', ['assigned', 'confirmed', 'waiting']),
            ])

            # Validar si ya hay otra recepción abierta con el mismo producto
            found = False
            for picking in pickings:
                for m in picking.move_ids:
                    if m.product_id == move.product_id:
                        found = True
                        break
                if found:
                    break

            if not found:
                # Aumentar cantidad temporalmente para que se genere recepción
                original_qty = purchase_line.product_qty
                purchase_line.product_qty += move.product_uom_qty
                purchase_order.button_confirm()  # fuerza regenerar recepción
                _logger.info(f"Generada nueva recepción por devolución de {move.product_id.name}")

                # Restaurar a cantidad original
                purchase_line.product_qty = original_qty

        return res
