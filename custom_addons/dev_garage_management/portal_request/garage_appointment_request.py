from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import werkzeug
from datetime import datetime, timedelta
import logging
from odoo.fields import Date
import re

_logger = logging.getLogger(__name__)


class AppointmentRequestWeb(CustomerPortal):


    # @http.route('/create/appointment', auth='public', website=True, type='http', csrf_token=True)
    # def create_appointment(self, **kw):
    #     values = self.get_default_data_contact(kw)
    #     employee = request.env['hr.employee'].sudo().search([])
    #     values.update({
    #         'employees': employee,
    #     })
    #     return request.render('dev_dental_clinic_management.website_appointment_requests', values)

    # def get_default_data_contact(self, kw=None):
    #     """This method for set image from appointment"""
    #     appointments = request.env['dc.dentist.speciality'].sudo().search([])

    #     for appt in appointments:
    #         if appt.image_1920 and isinstance(appt.image_1920, bytes):
    #             appt.image_1920 = appt.image_1920.decode('utf-8')
    #     return {'appointments': appointments}

    @http.route(['/fetch_date'], type='json', methods=['POST'], website=True, auth="public", csrf_token=False)
    def fetch_date(self, **post):
        """This Method for Fetch data"""
        selected_date = post.get('selected_date')
        selected_day = post.get('selected_day')
        selected_user_id = post.get('selected_user_id')
        selected_appointment = post.get('appointment_id')

        if not selected_date or not selected_day:
            return {'error': 'Missing required fields'}

        normalized_day = selected_day.lower()

        # Build domain for time.slot.line using fields directly on time.slot.line
        time_slot_line_domain = [
            ('day', '=', normalized_day)
        ]
        if selected_appointment:
            time_slot_line_domain.append(('service_id', '=', int(selected_appointment)))
        if selected_user_id:
            time_slot_line_domain.append(('user_ids', 'in', [selected_user_id]))

        time_slot_lines = request.env['time.slot.line'].sudo().search(time_slot_line_domain)

        # Find booked slots for the selected_date
        booked_events = request.env['calendar.event'].sudo().search([
            ('booking_date', '=', selected_date),
            ('time_slot_ids', '!=', False),
        ])

        booked_time_slot_ids = set()
        for event in booked_events:
            booked_time_slot_ids.update(event.time_slot_ids.ids)

        result = [{
            'id': slot.id,
            'name': slot.name,
            'is_booked': slot.id in booked_time_slot_ids
        } for slot in time_slot_lines]

        return result

    @http.route(['/general_appointment'], type='http', auth="public", methods=['POST'], website=True, csrf_token=True)
    def appointment_step1(self, appointment_id=None, **post):
        # If appointment_id is passed as POST data, use it
        if not appointment_id:
            appointment_id = post.get('appointment_id')

        appointment = request.env['dev.machine.service'].sudo().browse(int(appointment_id)) if appointment_id else None

        if not appointment or not appointment.exists():
            return request.not_found()  # Or render a fallback page

        slot_pool = request.env['time.slot.line'].sudo().search([])
        return request.render("dev_garage_management.website_appointment_requests_form2", {
            'slot_details': slot_pool,
            'appointment': appointment,  # pass the appointment record
            
        })
        
    # def get_default_data_gender(self):
    #     values = {}
    #     values['gender']=['Male','Female','Other']   
    #     return values    
        

    @http.route(['/appointment_form2'], type='http', auth="public", methods=['POST'], website=True, csrf_token=True)
    def appointment_step2(self, **post):
        appointment_id = post.get('appointment_id')
        
        appointment = None
        if appointment_id and appointment_id.isdigit():
            appointment = request.env['dev.machine.service'].sudo().browse(int(appointment_id))

        selected_slot_id = post.get('selected_slot_id')
        slot_record = None
        slot_name = ''
        if selected_slot_id:
            slot_record = request.env['time.slot.line'].sudo().browse(int(selected_slot_id))
            if slot_record.exists():
                slot_name = slot_record.name
        user_timezone = 'UTC'  # Default fallback

        # service_ids=request.env['dev.machine.service'].sudo().search([])
        service_type=request.env['fleet.service.type'].sudo().search([])
        vehicle_model_ids=request.env['fleet.vehicle.model'].sudo().search([])


        
            
        return request.render("dev_garage_management.website_appointment_requests_form3", {
            'appointment_id': appointment_id,
            'request_date': post.get('request_date'),
            'slot_details': selected_slot_id,
            'selected_slot_name': slot_name,
            'emp_id': post.get('emp_id'),
            'emp_name': post.get('emp_name'),
            'time_slot_name': post.get('time_slot_name'),
            'appointment_name': appointment.name,
            'appointment_location':appointment.location,
            # 'appointment_service_time': appointment.service_time,
            'appointment_fees': appointment.service_charge_amount,
            'appointment_type': appointment.appointment_type,
            # 'appointment_img': '/web/image/dev.machine.service/%s/image_1920' % appointment.id,
            'appointment': appointment,
            'user_timezone': user_timezone,
            'vehicle_model_id':vehicle_model_ids,
            'service_type':service_type
            
        })

    # @http.route('/get_user_timezone', type='json', auth='public')
    # def get_user_timezone(self, user_id):
    #     user = request.env['hr.employee'].sudo().browse(int(user_id))
    #     return {
    #         'timezone': user.tz or 'UTC'
    #     }

    @http.route(['/appointment_form3'], type='http', auth="public", methods=['POST'], website=True, csrf_token=True)
    def appointment_step4(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.env

        selected_user_id = post.get('selected_user_id')
        appointment_id = post.get('appointment_id')
        emp_id = post.get('emp_id')
        selected_slot_id = post.get('selected_slot_id')

        selected_date_str = post.get('request_date')
        if not selected_date_str:
            # Use today's date if none selected
            selected_date_str = Date.today().strftime("%Y-%m-%d")

        final_selected_date_str = datetime.strptime(selected_date_str, "%Y-%m-%d")

        domain = []
        partner = request.env['res.partner'].sudo().search(domain, limit=1)

        if not partner:
            partner = request.env['res.partner'].sudo().create({
                'name': post.get('contact_name') or "Guest",
            })

        total_charge = post.get('total_charge')
        time_slot = request.env['time.slot.line'].sudo().search([('id', '=', selected_slot_id)], limit=1)
        start_datetime = None
        end_datetime = None

        if time_slot and time_slot.name:
            try:
                slot_times = re.split(r'\s*[-–—]\s*', time_slot.name.strip())
                if len(slot_times) == 2:
                    start_time_test = slot_times[0].strip()
                    end_time_test = slot_times[1].strip()

                    # Combine with date and convert to datetime
                    new_check_in_datetime = datetime.strptime(f"{selected_date_str} {start_time_test}",
                                                              "%Y-%m-%d %H:%M")
                    new_check_out_datetime = datetime.strptime(f"{selected_date_str} {end_time_test}", "%Y-%m-%d %H:%M")

                    # Adjust to UTC if your local time is UTC+5:30
                    start_datetime = new_check_in_datetime - timedelta(hours=5, minutes=30)
                    end_datetime = new_check_out_datetime - timedelta(hours=5, minutes=30)
            except Exception as e:
                print("Error parsing and adjusting datetime:", e)
        # If start or end datetime is still None, set default (e.g. today + 9:00 to 10:00)
        if not start_datetime or not end_datetime:
            now = datetime.utcnow()
            start_datetime = now.replace(hour=9, minute=0, second=0, microsecond=0)
            end_datetime = now.replace(hour=10, minute=0, second=0, microsecond=0)
        contact_name = post.get('contact_name')
        reason = post.get('description')
        mobile_number = post.get('mobile')
        email = post.get('email')
        appointment_rec = request.env['dev.machine.service'].sudo().browse(int(appointment_id))
        customer_type = post.get('customer_type', 'new')
        customer_id = False
        if email and mobile_number:
            customer = request.env['res.partner'].sudo().search([
                ('email', '=', email),
                ('phone', '=', mobile_number)
            ], limit=1)
        else:
            customer = False
        if customer:
            # Match found — treat as existing
            customer_type = 'existing'
            customer_id = customer.id
        else:
            # No match — treat as new
            new_partner = request.env['res.partner'].sudo().create({
                'name': contact_name,
                'email': email,
                'phone': mobile_number,
            })
            customer_type = 'new'
            customer_id = new_partner.id
        #fees_value = appointment_rec.service_charge_amount if appointment_rec.exists() else 0  # correct field here
       
        
        
        	
        	
        domain = [('email', '=', email)]
        partner = request.env['res.partner'].sudo().search(domain, limit=1)


        # Step 3: If not found, create a new partner
        if not partner:
            partner = request.env['res.partner'].sudo().create({
					'name': contact_name,
					'email': email,
					'phone': mobile_number,
					 
        	})    

        # vehicle_type_id = post.get('vehicle_type')
        # service_type_id = post.get('service_type')

        vehicle_type_id = request.env['fleet.vehicle.model'].sudo().browse(int(post['vehicle_type']))
    
        service_type_id=request.env['fleet.service.type'].sudo().browse(int(post['service_type']))
             	
        	
        print("selected_user_id===============",selected_user_id)	 
        	 	
        appointment_request_id = request.env['calendar.event'].sudo().create({
            'name': contact_name,
            'description': reason,
            'mobile_number': mobile_number,
            'email': email,
            'partner_id': partner.id,
            'booking_date': final_selected_date_str,

            # 'fess_fees': fees_value,  # target field in calendar.event
            'time_slot_ids': [(6, 0, [time_slot.id])] if time_slot else [],
            'start': start_datetime,
            'stop': end_datetime,
            # 'appointment_id':'appointment_rec.id',
            'customer_type': customer_type,
            'customer_nm':contact_name,
            'customer_id': customer_id,
            'product_id':vehicle_type_id.id,
            'machine_name':vehicle_type_id.name,
            'demage':post.get('damage'),
            'service_id':appointment_rec.id,
            'service_type_id':service_type_id.id,
            'repair_issue':post.get('issue'),
            'repair_reason':post.get('reason'),
            

            
            # 'user_id': int(selected_user_id) if selected_user_id else False,
            
            
            'attendee_ids': [(0, 0, {
                'partner_id': partner.id,
                'email': email,
                'phone': mobile_number,
                    })],
                    
                })
        print('=====================appoint_ment=============',appointment_request_id)
            
        return request.render("dev_garage_management.website_appointment_request_thank_you", {'dev_company':appointment_request_id.company_id , 'reference_number': appointment_request_id.ref_name })
