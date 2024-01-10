# -*- coding: utf-8 -*-
# from odoo import http


# class Trazabilidad(http.Controller):
#     @http.route('/trazabilidad/trazabilidad', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/trazabilidad/trazabilidad/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('trazabilidad.listing', {
#             'root': '/trazabilidad/trazabilidad',
#             'objects': http.request.env['trazabilidad.trazabilidad'].search([]),
#         })

#     @http.route('/trazabilidad/trazabilidad/objects/<model("trazabilidad.trazabilidad"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('trazabilidad.object', {
#             'object': obj
#         })
