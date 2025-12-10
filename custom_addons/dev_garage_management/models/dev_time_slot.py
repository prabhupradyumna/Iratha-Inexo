from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class TimeSlot(models.Model):
    _name = 'time.slot'
    _description = 'Appointment Time Slots'
    _rec_name = 'day'

    day = fields.Selection([
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ], string="Day")
    slot_duration = fields.Integer('Slot Duration')
    start_time = fields.Float(string='Start Time (24H Format)')
    end_time = fields.Float(string='End Time (24H Format)')
    active = fields.Boolean(string='Active', default=True)
    slot_ids = fields.One2many('time.slot.line', 'time_slot_id', string='Generated Slots')
    service_id = fields.Many2one('dev.machine.service', string="Service")
    total_slot_count = fields.Integer(string='Total Slot Count', compute='_compute_total_slot_count', store=True)

    @api.depends('slot_ids')
    def _compute_total_slot_count(self):
        for record in self:
            record.total_slot_count = len(record.slot_ids)

    @api.constrains('day', 'service_id')
    def _check_unique_day_per_service(self):
        for record in self:
            if not record.service_id:
                continue  # Skip validation if service_id is not set
            domain = [
                ('day', '=', record.day),
                ('service_id', '=', record.service_id.id),
            ]
            if record.id:
                domain.append(('id', '!=', record.id))
            existing = self.search_count(domain)
            if existing > 0:
                raise ValidationError(
                    "There can only be one time slot per day for the same service."
                )

    def float_to_time(self, float_time):
        hours = int(float_time)
        minutes = int((float_time - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def action_generate_slots(self):
        if self.slot_ids:
            self.slot_ids.unlink()

        # Use custom slot duration from integer field
        slot_minutes = self.service_id.slot_duration or 60  # fallback to 60 if not set

        buffer_minutes = self.service_id.buffer_time or 0

        # Convert float time to datetime for start and end
        start_dt = datetime.combine(datetime.today(), datetime.min.time()).replace(
            hour=int(self.start_time),
            minute=int((self.start_time % 1) * 60)
        )
        end_dt = datetime.combine(datetime.today(), datetime.min.time()).replace(
            hour=int(self.end_time),
            minute=int((self.end_time % 1) * 60)
        )

        while start_dt + timedelta(minutes=slot_minutes) <= end_dt:
            end_slot = start_dt + timedelta(minutes=slot_minutes)
            slot_name = f"{start_dt.strftime('%H:%M')} – {end_slot.strftime('%H:%M')}"

            self.env['time.slot.line'].create({
                'name': slot_name,
                'time_slot_id': self.id,
                'day': self.day,
                'service_id': self.service_id.id,
                
            })

            start_dt = end_slot + timedelta(minutes=buffer_minutes)


class TimeSlotLine(models.Model):
    _name = 'time.slot.line'
    _description = 'Generated Time Slot'

    name = fields.Char(string='Time Slot')
    time_slot_id = fields.Many2one('time.slot', string='Time Slot', ondelete="cascade")
    user_ids = fields.Many2many('hr.employee',
        string="Dentist"
    )
    
    day = fields.Selection([
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ], string="Day")
    service_id = fields.Many2one('dev.machine.service', string="Service")
