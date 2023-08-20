# -*- coding: utf-8 -*-
# from odoo import http


# class InventoryFeilds(http.Controller):
#     @http.route('/inventory_feilds/inventory_feilds', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_feilds/inventory_feilds/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_feilds.listing', {
#             'root': '/inventory_feilds/inventory_feilds',
#             'objects': http.request.env['inventory_feilds.inventory_feilds'].search([]),
#         })

#     @http.route('/inventory_feilds/inventory_feilds/objects/<model("inventory_feilds.inventory_feilds"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_feilds.object', {
#             'object': obj
#         })
