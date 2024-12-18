from odoo import models, fields, api

class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    button_pressed = fields.Boolean(string="Botón Presionado")

    #def mostrar_lotes(self):
    #    for move in self:
    #        lots = self.env['stock.lot'].search([('product_id', '=', move.product_id.id)])
    #        move_line_vals_list = []
    #        for lot in lots:
    #            move_line_vals = {
    #                'company_id': move.company_id.id,
    #                'date': fields.Datetime.now(),
    #                'location_dest_id': move.location_dest_id.id,
    #                'location_id': move.location_id.id,
    #                'product_id': move.product_id.id,
    #                'product_uom_id': move.product_id.uom_id.id,
    #                'qty_done': lot.product_qty,
    #                'reserved_uom_qty': lot.product_qty,
    #                'lot_id': lot.id,
    #            }
    #            move_line_vals_list.append((0, 0, move_line_vals))

    #        move.write({'move_line_ids': move_line_vals_list})
    #segunda  funciona super bien pero falta
    #def mostrar_lotes(self):
    #    for move in self:
            # Buscar los lotes relacionados con el producto y ordenarlos por cantidad descendente y fecha de creación ascendente
    #        lots = self.env['stock.lot'].search([('product_id', '=', move.product_id.id), ('product_qty', '>', 0.00)],
    #                                            order='product_qty DESC, create_date ASC')
    #        move_line_vals_list = []
    #        for lot in lots:
    #            move_line_vals = {
    #                'company_id': move.company_id.id,
    #                'date': fields.Datetime.now(),
    #                'location_dest_id': move.location_dest_id.id,
    #                'location_id': move.location_id.id,
    #                'product_id': move.product_id.id,
    #                'product_uom_id': move.product_id.uom_id.id,
    #                'qty_done': lot.product_qty,
    #                'reserved_uom_qty': lot.product_qty,
    #                'lot_id': lot.id,
    #            }
    #            move_line_vals_list.append((0, 0, move_line_vals))

    #        move.write({'move_line_ids': move_line_vals_list})


    #tercera ya casi completa
    #def mostrar_lotes(self):
    #    for move in self:
            # Buscar los lotes relacionados con el producto y ordenarlos
    #        lots = self.env['stock.lot'].search([('product_id', '=', move.product_id.id), ('product_qty', '>', 0.00)])
    #        grouped_lots = {}  # Diccionario para agrupar los lotes por fecha de creación
    #        for lot in lots:
    #            key = lot.create_date.date()
    #            if key not in grouped_lots:
    #                grouped_lots[key] = []
    #            grouped_lots[key].append(lot)

    #        sorted_lots = []
            # Ordenar los grupos de lotes
    #        for key, group in sorted(grouped_lots.items()):
                # Ordenar los lotes dentro de cada grupo por cantidad (product_qty)
    #            sorted_group = sorted(group, key=lambda x: x.product_qty, reverse=True)
    #            sorted_lots.extend(sorted_group)

    #        move_line_vals_list = []
    #        for lot in sorted_lots:
    #            move_line_vals = {
    #                'company_id': move.company_id.id,
    #                'date': fields.Datetime.now(),
    #                'location_dest_id': move.location_dest_id.id,
    #                'location_id': move.location_id.id,
    #                'product_id': move.product_id.id,
    #                'product_uom_id': move.product_id.uom_id.id,
    #                'qty_done': lot.product_qty,
    #                'reserved_uom_qty': lot.product_qty,
    #                'lot_id': lot.id,
    #            }
    #            move_line_vals_list.append((0, 0, move_line_vals))

    #        move.write({'move_line_ids': move_line_vals_list})
    #ultimo ya casi bien
    def mostrar_lotes(self):
         for move in self:
            # Buscar los lotes relacionados con el producto y ordenarlos
            lots = self.env['stock.lot'].search([('product_id', '=', move.product_id.id), ('product_qty', '>', 0.00)])
            grouped_lots = {}  # Diccionario para agrupar los lotes por fecha de creación
            for lot in lots:
                key = lot.create_date.date()
                if key not in grouped_lots:
                    grouped_lots[key] = []
                grouped_lots[key].append(lot)

            sorted_lots = []
            # Ordenar los grupos de lotes
            for key, group in sorted(grouped_lots.items()):
                # Ordenar los lotes dentro de cada grupo por cantidad (product_qty)
                sorted_group = sorted(group, key=lambda x: x.product_qty, reverse=True)
                sorted_lots.extend(sorted_group)

            total_qty = sum(lot.product_qty for lot in sorted_lots)
            remaining_qty = move.product_uom_qty

            move_line_vals_list = []
            for lot in sorted_lots:
                if remaining_qty <= 0:
                    break
                if lot.product_qty >= remaining_qty:
                    qty_done = remaining_qty
                    remaining_qty = 0
                else:
                    qty_done = lot.product_qty
                    remaining_qty -= lot.product_qty
                move_line_vals = {
                    'company_id': move.company_id.id,
                    'date': fields.Datetime.now(),
                    'location_dest_id': move.location_dest_id.id,
                    'location_id': move.location_id.id,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_id.uom_id.id,
                    'qty_done': qty_done,
                    'reserved_uom_qty': qty_done,
                    'lot_id': lot.id,
                }
                move_line_vals_list.append((0, 0, move_line_vals))

            move.write({'move_line_ids': move_line_vals_list})
            move.write({'button_pressed': True})




class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'


    @api.model
    def create(self, vals):
        if 'lot_id' in vals and 'qty_done' not in vals:
            lot = self.env['stock.lot'].browse(vals['lot_id'])
            vals['qty_done'] = lot.product_qty
        return super(StockMoveLineInherit, self).create(vals)
