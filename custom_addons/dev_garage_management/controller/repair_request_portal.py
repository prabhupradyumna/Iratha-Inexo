from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import werkzeug

class RepairRequestPortal(CustomerPortal):
    @http.route('/create/repair_request', auth='public', website=True, type='http', csrf_token=True)
    def create_repair_request(self, **kw):
        values = self.get_default_data_contact()
        return request.render('dev_garage_management.repair_request_form',values)


    def get_default_data_contact(self):
        vehicle_model_id = request.env['fleet.vehicle.model'].sudo().search([])
        service_id = request.env['dev.machine.service'].sudo().search([])
        service_type_id = request.env['fleet.service.type'].sudo().search([])
        values = {}
        if vehicle_model_id:
            values['vehicle_model_ids']=vehicle_model_id
        if service_id:
            values['service_ids']=service_id
        if service_type_id:
            values['service_type_ids']=service_type_id
        values['type_type']=['Low','Normal','High','Very High']
        return values
    
    @http.route(['/repair_request'], type='http', auth="public", methods=['POST'], website=True)
    def repair_request_submitted(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.env
        
        # Check if required parameters are present
        if 'vehicle_model' in post and 'service' in post and 'service_type' in post  and 'email' in post and 'phone' in post:

            vehicle_model_id = request.env['fleet.vehicle.model'].sudo().browse(int(post['vehicle_model']))
            service_id = request.env['dev.machine.service'].browse(int(post['service']))
            service_type_id = request.env['fleet.service.type'].browse(int(post['service_type']))
            partner = request.env.user.partner_id
            lead_name = "Request of " + post['contact_name'] + "[ " + vehicle_model_id.brand_id.name + "/" + vehicle_model_id.name  + " ]"

            # Check if records exist before accessing their attributes
            if service_id:
                repair_request_id = pool['crm.lead'].sudo().create({
                    'contact_name': post['contact_name'],
                    'name': lead_name ,
                 #   'customer_id': partner.id,
                    'email_from': post['email'],
                    'phone': post['phone'],
                    'product_id': vehicle_model_id.id,
                 #   'machine_name': post['vehicle_name'],
                    'repair_issue': post['repair_issue'],
                    'repair_reason': post['repair_reason'],
                    'demage': post['demage'],
                    'service_type_id': service_type_id.id,
                    'service_id': service_id.id,
                 #   'priority':final_type,
                    'type':'lead',
                })
                repair_request_id.onchange_machine()
        
        return werkzeug.utils.redirect('/request-thank-you')
    
    @http.route(['/request-thank-you'], type='http', auth="public", website=True)
    def request_thank_you(self, **post):
        return request.render('dev_garage_management.repair_request_submitted_greeting')



