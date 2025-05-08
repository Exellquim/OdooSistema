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

    camas_x_pallet = fields.Float(
        string="Camas por Pallet",
        compute="_compute_pallet_metrics",
        store=True
    )
    cajas_x_pallet = fields.Float(
        string="Cajas por Pallet",
        compute="_compute_pallet_metrics",
        store=True
    )
    unidades_sku_x_pallet = fields.Float(
        string="Unidades SKU por Pallet",
        compute="_compute_pallet_metrics",
        store=True
    )

    @api.depends('product_uom_qty', 'product_id.x_studio_unidades_sku_x_pallet', 'product_id.x_studio_cajas_x_pallet')
    def _compute_pallet_metrics(self):
        for move in self:
            unidades_x_pallet = move.product_id.x_studio_unidades_sku_x_pallet or 1.0
            cajas_por_pallet = move.product_id.x_studio_cajas_x_pallet or 1.0
            unidades_por_caja = move.x_studio_unidades_x_caja or 1.0

            # ----------------------------
            # Cálculo UNIDADES SKU X PALLET
            # ----------------------------
            # Variable 1: cuántos pallets caben
            pallet_count_float = move.product_uom_qty / unidades_x_pallet
            pallet_count_entero = int(pallet_count_float)

            # Variable 2: pallet_count_entero * unidades_x_pallet
            total_full_pallet_units = pallet_count_entero * unidades_x_pallet

            # Resultado: sobrante
            sobrante = move.product_uom_qty - total_full_pallet_units

            move.unidades_sku_x_pallet = sobrante

            # ----------------------------
            # Cálculo CAJAS X PALLET
            # ----------------------------
            if cajas_por_pallet:
                move.cajas_x_pallet = sobrante / cajas_por_pallet
            else:
                move.cajas_x_pallet = 0.0

            # ----------------------------
            # Cálculo CAMAS X PALLET
            # ----------------------------
            if cajas_por_pallet:
                move.camas_x_pallet = move.unidades_sku_x_pallet / unidades_por_caja
            else:
                move.camas_x_pallet = 0.0

