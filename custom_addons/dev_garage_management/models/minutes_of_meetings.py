from odoo import api, models, fields
from datetime import datetime, timedelta
from odoo.tools import format_datetime

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'
    _order='ref_name desc'

   

    customer_type = fields.Selection(selection=[('new', 'New Customer'), ('existing', 'Existing Customer')],
                                    default='new', string='Customer Type', required=True, tracking=1)

    customer_id = fields.Many2one('res.partner', string="Customer", tracking=1)
    

    product_id = fields.Many2one('fleet.vehicle.model', string='Vehicle Model')
    machine_name = fields.Char('Vehicle Name')
    demage = fields.Text('Damage')
    service_id = fields.Many2one('dev.machine.service', string='Service')
    service_type_id = fields.Many2one('fleet.service.type', string='Service Type')
    repair_issue = fields.Char('Repair Issue')
    repair_reason = fields.Char('Reason For Repair')
    # job_card = fields.Integer(string='Job Card ', compute='job_card_count')
    fess_fees = fields.Float(string="Fees")
    time_slot_ids = fields.Many2many(
        'time.slot.line',
        'calendar_event_time_slot_rel',
        'event_id',
        'slot_id',
        string='Time Slots'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='draft', string="State")
    booking_date = fields.Date(string='Booking Date')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=1,
                                 required=True)
    garage_ids = fields.One2many('dev.repair.request', 'calendar_event_id', string="Garage Request")
    garage_req_count = fields.Integer(string="Garage Request Count", compute="_compute_garage_req_case_count")
    customer_nm = fields.Char(string="Customer Name", required=True, tracking=1)
    email = fields.Char('Email')
    mobile_number = fields.Char('Mobile Number')
    ref_name = fields.Char(string='Appointment Reference', required=True, copy=False, readonly=True, default='New')


#    @api.model
#    def create(self, vals):
#        if vals.get('ref_name', 'New') == 'New':
#            vals['ref_name'] = self.env['ir.sequence'].next_by_code('calendar.event') or 'New'
#        return super(CalendarEvent, self).create(vals)	

   
    @api.model
    def create(self, vals_list):
        for vals in vals_list:  
            if vals.get('ref_name', 'New') == 'New':
                vals['ref_name'] = self.env['ir.sequence'].next_by_code('calendar.event') or 'New'
        return super(CalendarEvent, self).create(vals_list)	

    def action_confirm(self):
        for record in self:
            template = self.env.ref('dev_garage_management.appointment_confirmation_email_template_id')
            if template:
                template.send_mail(record.id, force_send=True)
            record.state = 'confirm'


    @api.depends('garage_ids')
    def _compute_garage_req_case_count(self):
        for rec in self:
            rec.garage_req_count = len(rec.garage_ids)

    
    @api.onchange('product_id')
    def onchange_machine(self):
        if self.product_id:
            self.machine_name = self.product_id.name


    def action_create_job_card(self):
        if self.customer_type == 'new':

            new_customer_values = {
                'name': self.customer_nm,
                'email': self.email,
                'phone': self.mobile_number or '',
                
            }
            customer_partner_id = self.env['res.partner'].sudo().create(new_customer_values)
            customer = customer_partner_id.id if customer_partner_id else False
        else:
            customer = self.customer_id.id if self.customer_id else False

        if not customer:
            return

        # Check if a case already exists for the patient
        existing_req = self.env['dev.repair.request'].search([('customer_id', '=', customer)], limit=1)

        if existing_req:
            existing_req.calendar_event_id = self.id
        else:
            # Create a new case only if none exists
            vals = {'desc': self.name,
                'customer_id': self.partner_id.id,
                # 'priority': self.priority,
                'email': self.email,
                'phone': self.mobile_number,
                'product_id': self.product_id.id,
                'machine_name': self.machine_name,
                'demage': self.demage,
                'service_id': self.service_id.id,
                'service_type_id': self.service_type_id.id,
                # 'team_id': self.team_id.id,
                'notes': self.repair_issue + "\n" + self.repair_reason,
                'request_date': self.booking_date,
                'calendar_event_id': self.id
                
                }
            aa=  self.env['dev.repair.request'].create(vals)
            print("aa====================",aa)

        if customer and self.email:
            existing_user = self.env['res.users'].sudo().search([('partner_id', '=', customer)], limit=1)
            if not existing_user:
                user_vals = {
                    'name': self.customer_nm,
                    'login': self.email,
                    'email': self.email,
                    'partner_id': customer,
                    'group_ids': [(6, 0, [self.env.ref('base.group_portal').id])]  # Assign Portal User Group
                }
                new_user = self.env['res.users'].sudo().create(user_vals)
        self.state = 'done'


    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_done(self):
        for record in self:
            record.state = 'done'

    def action_reset_to_draft(self):
        for record in self:
            record.state = 'draft'



   




    def action_open_repair_request(self):
        self.ensure_one()
        return {
            'name': 'Garage Request',
            'type': 'ir.actions.act_window',
            'res_model': 'dev.repair.request',
            'view_mode': 'list,form',
            'domain': [('calendar_event_id', '=', self.id)],
            'context': {'default_calendar_event_id': self.id}
        }

