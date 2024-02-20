import time
from odoo import fields, models, api, exceptions
from datetime import timedelta
from dateutil.parser import parse




class Asistencia(models.Model):

    _inherit = 'hr.attendance'

    accion = fields.Char(string="Salida a Comer", readonly=True)
    eat_in = fields.Datetime(string="Salida a Comer", store=True,readonly=True)
    eat_in_nuevo = fields.Datetime(string="Salida a Comer23", store=True, readonly=True)
    check_out_final = fields.Datetime(string="Salida primetra", compute="_compute_check_out2", store=True, readonly=True)
    check2 = fields.Datetime(string="Entrada", compute="_compute_check2", store=True)
    check_out2 = fields.Datetime(string="Salida1", compute="_compute_check_out2", store=True)
    encuentros = fields.Char(string="Encuentros Regreso de comer", compute='_compute_out_in', store=True)
    encuentros_salida = fields.Integer('Encuentros Salida', compute='_compute_eat_out', store=True)
    eat_out2 = fields.Datetime(string='Regreso de Comer', compute='_compute_eat_out2', store=True)
    horas_laborales = fields.Float(string='Horas laborales',  compute='_compute_horas_laborales',store=True, readonly=True)
    cambio = fields.Char(string='Cambio', store=True,compute='verificar_y_asignar_numero', readonly=True)
    registros_por_empleado = fields.Integer(string="Registros por Empleado", store=True)
    boton = fields.Char(string="Boton", store=True)





    @api.depends('check_in', 'employee_id')
    def _compute_out_in(self):
        for record in self:
            check_in_date = fields.Date.to_string(record.check_in.date())
            next_day = record.check_in.date() + timedelta(days=1)
            next_day_str = fields.Date.to_string(next_day)

            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', check_in_date),
                ('check_in', '<', next_day_str),
            ]

            count = self.search_count(domain)

            record.encuentros = count



    @api.depends('check_out', 'employee_id')
    def _compute_eat_out(self):
        for record in self:
            if record.check_out:
                check_out_date = fields.Date.to_string(record.check_out.date())
                next_day = record.check_out.date() + timedelta(days=1)
                next_day_str = fields.Date.to_string(next_day)

                domain = [
                    ('employee_id', '=', record.employee_id.id),
                    ('check_out', '>=', check_out_date),
                    ('check_out', '<', next_day_str),
                ]

                count = self.search_count(domain)

                record.encuentros_salida = count
            else:
                record.encuentros_salida = 0



    @api.depends('check_in', 'employee_id')
    def _compute_out_in2(self):
        for record in self:
            check_in_date = fields.Date.to_string(record.check_in.date())
            next_day = record.check_in.date() + timedelta(days=1)
            next_day_str = fields.Date.to_string(next_day)

            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', check_in_date),
                ('check_in', '<', next_day_str),
            ]

            earliest_check_in = self.search(domain, order='check_in', limit=1)

            second_earliest_check_in = self.search(domain + [('id', '!=', earliest_check_in.id)], order='check_in',
                                                   limit=1)

            if earliest_check_in:

                record.check2 = earliest_check_in.check_in
            else:

                record.check2 = False

    #@api.onchange('eat_out2')
    #def _onchange_eat_out2(self):
        #for record in self:
            #if record.eat_out2:  # Verificar si eat_out2 tiene un valor
                #record.eat_in = record.check_out_final
            #else:
                #record.eat_in = False




    @api.depends('check_in', 'employee_id')
    def _compute_check2(self):
        for record in self:
            check_in_date = fields.Date.to_string(record.check_in.date())
            next_day = record.check_in.date() + timedelta(days=1)
            next_day_str = fields.Date.to_string(next_day)

            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', check_in_date),
                ('check_in', '<', next_day_str),
            ]

            earliest_check_in = self.search(domain, order='check_in', limit=1)

            if earliest_check_in:
                # Asignar el valor de check_in al campo check2
                record.check2 = earliest_check_in.check_in
            else:
                record.check2 = False


    @api.depends('check_out', 'employee_id')
    def _compute_check_out2(self):
        for record in self:
            if not record.eat_in:  # Verificar si eat_in ya tiene un valor
                check_in_date = fields.Date.to_string(record.check_in.date())
                next_day = record.check_in.date() + timedelta(days=1)
                next_day_str = fields.Date.to_string(next_day)

                domain = [
                    ('employee_id', '=', record.employee_id.id),
                    ('check_out', '>=', check_in_date),
                    ('check_out', '<', next_day_str),
                ]

                earliest_check_in = self.search(domain, order='check_out', limit=1)

                if earliest_check_in:

                    record.check_out_final = earliest_check_in.check_out
                else:
                    record.check_out_final = False

    # calculo pendiente
    @api.depends('check_out', 'employee_id')
    def _compute_out_out(self):
        for record in self:
            if record.check_out:
                check_out_date = fields.Date.to_string(record.check_out.date())
                next_day = record.check_out.date() + timedelta(days=1)
                next_day_str = fields.Date.to_string(next_day)

                domain = [
                    ('employee_id', '=', record.employee_id.id),
                    ('check_out', '>=', check_out_date),
                    ('check_out', '<', next_day_str),
                ]

                earliest_check_out = self.search(domain, order='check_out', limit=1)

                record.eat_in = earliest_check_out.check_out if earliest_check_out else False
            else:
                record.eat_in = False

    # calculo para retomar la hora de regreso a comer
    @api.depends('check_in', 'employee_id')
    def _compute_eat_out2(self):
        for record in self:
            if record.check_in:
                check_in_date = fields.Date.to_string(record.check_in.date())
                next_day = record.check_in.date() + timedelta(days=1)
                next_day_str = fields.Date.to_string(next_day)

                domain = [
                    ('employee_id', '=', record.employee_id.id),
                    ('check_in', '>=', check_in_date),
                    ('check_in', '<', next_day_str),
                ]

                earliest_check_in = self.search(domain, order='check_in', limit=2)

                record.eat_out2 = earliest_check_in[1].check_in if len(earliest_check_in) > 1 else False
            else:
                record.eat_out2 = False


  #accion del boton actualizar
    def buscar_y_eliminar_registro(self):
        if self.check_in:
            fecha_sin_hora = fields.Datetime.from_string(self.check_in).date()

            registros_similares = self.search([
                ('employee_id', '=', self.employee_id.id),
                ('check_in', '>=', fecha_sin_hora),
                ('check_in', '<', fecha_sin_hora + timedelta(days=1)),
            ], order='check_in')

            if len(registros_similares) >= 2:
                primer_registro = registros_similares[0]
                primer_registro.unlink()
                 # Llama al método de cálculo en el registro actual después de eliminar el otro




    #def buscar_y_eliminar_registro(self):
        #if self.check_in:
            #fecha_sin_hora = fields.Datetime.from_string(self.check_in).date()

            #registros_similares = self.search([
              #  ('employee_id', '=', self.employee_id.id),
              #  ('check_in', '>=', fecha_sin_hora),
              #  ('check_in', '<', fecha_sin_hora + timedelta(days=1)),
            #], order='check_in')

            #if len(registros_similares) >= 2:
            #    primer_registro = registros_similares[0]
            #    segundo_registro = registros_similares[1]

                # Asignar el valor de check_out_final del primer registro al campo eat_in_nuevo del segundo registro
            #    segundo_registro.write({'eat_in_nuevo': primer_registro.check_out_final})

                # Eliminar el primer registro dentro de una transacción
            #    try:
            #        with api.Environment.manage():
            #           with api.Environment(self.env.cr, self.env.uid, self.env.context):
            #                primer_registro.unlink()

            #    except exceptions.AccessError:
                    # Manejar errores de acceso si es necesario
            #        pass




    def buscar_y_eliminar_registro_button(self):
        for record in self:
            record.buscar_y_eliminar_registro()
            record._compute_eat_in_nuevo()



            # calculo para horas laborales
    @api.depends('check2', 'check_out')
    def _compute_horas_laborales(self):
        for record in self:
            if record.check_in and record.check_out:
                tiempo_trabajo = record.check_out - record.check2
                horas_laborales = tiempo_trabajo.total_seconds() / 3600
                record.horas_laborales = horas_laborales
            else:
                record.horas_laborales = 0.0


    #calculo para campo cambio
    @api.depends('check_out')
    def _compute_cambio(self):
        for record in self:
            if record.check_out:
                record.cambio = '1'

            else:
                record.cambio = '0'


    # calculo para asignar numero segun registros
    @api.depends('check_out')
    def verificar_y_asignar_numero(self):
            if self.check_in:
                fecha_sin_hora = fields.Datetime.from_string(self.check_in).date()
                registros_similares = self.search([
                    ('employee_id', '=', self.employee_id.id),
                    ('check_in', '>=', fecha_sin_hora),
                    ('check_in', '<', fecha_sin_hora + timedelta(days=1)),
                ], order='check_in')

                if registros_similares:
                    self.cambio = 3
                else:
                    self.cambio = 1

    @api.depends('eat_in')
    def _compute_eat_in_nuevo(self):
        for record in self:
            if record.eat_in:  # Verifica si eat_in tiene un valor
                record.accion = record.eat_in
            else:
                record.accion = False  # O cualquier valor que desees establecer cuando eat_in no está definido



    # calculo para actualizar boton
    #@api.depends('cambio')
    #def _compute_actualizar_boton(self):
        #registros_3 = self.search_count([('cambio', '=', '3')])
        #if registros_3 >= 2:
            #self.buscar_y_eliminar_registro()
            #self.boton = 1
            #self.eat_in2 = self.check_out_final















