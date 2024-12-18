from odoo import models, fields, api
from operator import itemgetter


class StockMove(models.Model):
    """ Open wizard."""
    _inherit = 'stock.move'

    lote = fields.Html(string='Lotes')
    cantidad = fields.Html(string='Cantidad')
    datos = fields.Binary(string='Datos')
    Tabla_one2many = fields.One2many('stock.lot', 'move_id', string="Tabla")

    #def mostrar_lotes(self):
    #    for move in self:
            # Inicializamos una cadena para almacenar la información de los lotes
    #        lotes_info = ""

            # Obtenemos el ID del producto del movimiento
    #        product_id = move.product_id.id

            # Buscamos los lotes correspondientes al producto ordenados por fecha de creación
    #        lotes = self.env['stock.lot'].search([('product_id', '=', product_id)], order='create_date')

            # Recorremos los lotes encontrados
    #        for lote in lotes:
                # Agregamos la información del lote a la cadena
    #            lotes_info += f"Lote: {lote.name}"
    #            cantidad_info += f"Can:{lote.product_qty}\n"

            # Actualizamos los campos 'lote' y 'cantidad' con la información obtenida
    #        move.lote = lotes_info
    #        move.cantidad = cantidad_info

    #def actualizar_valores(self):
    # Suponiendo que product_id está disponible en el objeto StockMove
    #    product_id = self.product_id.id

    # Buscar todos los lotes correspondientes al product_id
    #    lots = self.env['stock.lot'].search([('product_id', '=', product_id)])

    # Verificar si se encontraron lotes
    #    if lots:
    # Ordenar los lotes por cantidad de producto en orden descendente
    #        sorted_lots = lots.sorted(key=lambda x: x.product_qty, reverse=True)

    # Inicializar la cantidad a cero
    #        qty_done = 0

    # Iterar sobre los lotes ordenados
    #        for lot in sorted_lots:
    # Si la cantidad del lote es menor o igual a la cantidad del movimiento de stock
    #            if lot.product_qty <= self.product_uom_qty:
    # Actualizar la cantidad hecha con la cantidad del lote
    #                qty_done = lot.product_qty
    #                break

    # Si no se encontró ningún lote con cantidad suficiente, usar la cantidad del primer lote
    #        if qty_done == 0:
    #            qty_done = sorted_lots[0].product_qty

    # Actualizar el campo lot_id de stock.move.line con el lot_id encontrado
    #        for move_line in self.move_line_ids:
    #            move_line.lot_id = sorted_lots[0].id  # Usar el primer lote para asignar el ID del lote
    # Actualizar el campo qty_done de stock.move.line con la cantidad del movimiento de stock
    #            move_line.qty_done = min(qty_done, self.product_uom_qty)







class StockLot(models.Model):
    _inherit = 'stock.lot'

    move_id = fields.Many2one('stock.move', string='Movimiento')
    lote = fields.Char(string='Lotes')
    cantidad = fields.Char(string='Cantidad')

    #def valor_lista(self):
        # Suponiendo que product_id está disponible en el objeto StockMove
    #    product_id = self.product_id.id

        # Buscar todos los lotes correspondientes al product_id
    #    lots = self.env['stock.lot'].search([('product_id', '=', product_id)])

        # Verificar si se encontraron lotes
    #    if lots:
            # Ordenar los lotes por cantidad de producto en orden descendente
    #        sorted_lots = lots.sorted(key=lambda x: x.product_qty, reverse=True)

            # Inicializar la cantidad a cero
    #        qty_done = 0

            # Iterar sobre los lotes ordenados
    #        for lot in sorted_lots:
                # Si la cantidad del lote es menor o igual a la cantidad del movimiento de stock
    #            if lot.product_qty <= self.product_uom_qty:
                    # Actualizar la cantidad hecha con la cantidad del lote
    #                qty_done = lot.product_qty
    #                break

            # Si no se encontró ningún lote con cantidad suficiente, usar la cantidad del primer lote
    #        if qty_done == 0:
    #            qty_done = sorted_lots[0].product_qty

            # Actualizar el campo lot_id de stock.move.line con el lot_id encontrado
    #        for move_line in self.move_line_ids:
    #            move_line.lot_id = sorted_lots[0].id  # Usar el primer lote para asignar el ID del lote
                # Actualizar el campo qty_done de stock.move.line con la cantidad del movimiento de stock
    #            move_line.qty_done = min(qty_done, self.product_uom_qty)



