# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz


class dev_machine_service(models.Model):
    _name = "dev.machine.service"
    _description = "Machine Service"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Name', required="1")
    code = fields.Char('Code')
    short_desc=fields.Text(string="Short Description")

    description = fields.Html(string='Description', default='')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=1,
                                    required=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=1,
                                required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    service_charge_amount = fields.Float(string='Service Charge', tracking=1)
    is_active = fields.Boolean("Is Publish" , default=False)
    # icon_image=fields.Char("Service Image Name")


    _tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]
    def _tz_get(self):
        return _tzs


    image_1920 = fields.Image("Image")
    location = fields.Char("Location")
    #    fees = fields.Float("Fees")
    appointment_type = fields.Selection([('online', 'Online'), ('offline', 'Offline')], default='online', string='Appointment Type')
#    user_tz_id = fields.Many2one('')
    user_timezone = fields.Char(
        string='User Timezone',
        default=lambda self: self.env.user.tz or 'UTC'
    )
    time_slot_ids = fields.One2many('time.slot', 'service_id', string='Generated Slots')
    time_slot_line_ids = fields.One2many('time.slot.line', 'service_id', string='Slots')
    slot_duration = fields.Integer('Slot Duration', help="Enter slot duration in minutes")
    #    start_time = fields.Float(string='Start Time', required=True)
    #    end_time = fields.Float(string='End Time', required=True)
    start_time = fields.Float(string='Start Time', required=True, default=9.0)  # 9 AM
    end_time = fields.Float(string='End Time', required=True, default=10.0)    # 10 AM

    time_slot_id = fields.Many2one('time.slot') 
    buffer_time = fields.Integer('Buffer Time',  help="Enter buffer time in minutes")
    mon = fields.Boolean(readonly=False)
    tue = fields.Boolean(readonly=False)
    wed = fields.Boolean(readonly=False)
    thu = fields.Boolean(readonly=False)
    fri = fields.Boolean(readonly=False)
    sat = fields.Boolean(readonly=False)
    sun = fields.Boolean(readonly=False)
    tz = fields.Selection(_tzs, string='Timezone', default=lambda self: self._context.get('tz'),
                            help="When printing documents and exporting/importing data, time values are computed according to this timezone.\n"
                                "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
                                "Anywhere else, time values are computed according to the time offset of your web client.")

    icon_image = fields.Selection([
        ('pms.png', 'Periodic Maintenance Service (PMS)'),
        ('inspection.png', 'Car Inspection & Diagnostics'),
        ('general.png', 'General Repairs'),
        ('engine.png', 'Engine Repair & Tuning'),
        ('battery.png', 'Battery Check & Replacement'),
        ('cooling.png', 'Cooling System Services'),
        ('clutch.png', 'Clutch & Transmission Repair'),
        ('brake.png', 'Brake Inspection & Replacement'),
        ('ac.png', 'AC Repair & Gas Refill'),
        ('electrical.png', 'Electrical System Diagnostics'),
        ('car_wash.png', 'Car Washing & Detailing'),
        ('interior_clean.png', 'Interior Vacuum & Cleaning'),
        ('polish.png', 'Polishing & Ceramic Coating'),
        ('glass_replace.png', 'Windshield & Glass Replacement'),
        ('paint.png', 'Paint Touch-ups & Full Body Paint'),
        
    ], string="Service Image Name", default='pms.png',)


    @api.constrains('start_time', 'end_time')
    def _check_times(self):
        for record in self:
            if record.start_time and record.end_time and record.end_time <= record.start_time:
                raise ValidationError("End Time must be greater than Start Time.")

    def action_generate_slots_appointment(self):
        if not self.start_time or not self.end_time:
            raise ValidationError("Please provide both Start Time and End Time before generating slots.")
        if not self.slot_duration:
            raise ValidationError("Please set a Slot Duration before generating slots.")
        self.ensure_one()
        weekday_map = {
            'mon': self.mon,
            'tue': self.tue,
            'wed': self.wed,
            'thu': self.thu,
            'fri': self.fri,
            'sat': self.sat,
            'sun': self.sun,
        }
        print("weekday_map========================", weekday_map)
       

        for day_code, is_selected in weekday_map.items():
            print("day_code========================", day_code, "is_selected========================", is_selected)
            if is_selected:
                values = {
                    'day': day_code,
                    'start_time': self.start_time,
                    'end_time': self.end_time,
                    'service_id': self.id,
                    'slot_duration': self.slot_duration,
   
                   
                }
                time_slot = self.env['time.slot'].create(values)
                time_slot.action_generate_slots()

    




    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
