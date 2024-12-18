# -*- coding: utf-8 -*-
# from odoo import http


# class Herencia(http.Controller):
#     @http.route('/herencia/herencia', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/herencia/herencia/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('herencia.listing', {
#             'root': '/herencia/herencia',
#             'objects': http.request.env['herencia.herencia'].search([]),
#         })

#     @http.route('/herencia/herencia/objects/<model("herencia.herencia"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('herencia.object', {
#             'object': obj
#         })
