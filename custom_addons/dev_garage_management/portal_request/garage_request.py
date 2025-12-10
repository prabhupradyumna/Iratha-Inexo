from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import werkzeug
from odoo import fields
from datetime import date
from datetime import datetime
import pytz


class GaragePortalrequest(CustomerPortal):

    @http.route('/garage_appointment', auth='public', website=True, type='http', csrf_token=True)
    def garage_request(self, **kw):

        
        services_ids=request.env['dev.machine.service'].sudo().search([('is_active', '=', True)])
        company_id=request.env.company

        values={
            'services_ids':services_ids,
            'company':company_id,
        }

        

    
        return request.render('dev_garage_management.garage_request_template',values)

    
    


    


