# from odoo import http


# class PartnerLedger(http.Controller):
#     @http.route('/partner_ledger/partner_ledger', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_ledger/partner_ledger/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_ledger.listing', {
#             'root': '/partner_ledger/partner_ledger',
#             'objects': http.request.env['partner_ledger.partner_ledger'].search([]),
#         })

#     @http.route('/partner_ledger/partner_ledger/objects/<model("partner_ledger.partner_ledger"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_ledger.object', {
#             'object': obj
#         })

