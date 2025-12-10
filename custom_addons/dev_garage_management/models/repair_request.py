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
from datetime import datetime
from odoo.exceptions import ValidationError
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta


class repair_request(models.Model):
    _name = "dev.repair.request"
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']
    _order = 'name desc'
    _description = "Repair Request"
    
    
    def _compute_access_url(self):
        super(repair_request, self)._compute_access_url()
        for repair in self:
            repair.access_url = '/my/job_card/%s' % (repair.id)
    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (_('Job Card'), self.name)
    
    
    @api.model
    def _get_default_team(self):
        team_id = self.env['crm.team'].search([('is_default','=',True)], limit=1)
        return team_id
        
        
    name = fields.Char('Name', copy=False, tracking=1)
    desc = fields.Char('Desc', required="1", tracking=1)
    customer_id = fields.Many2one('res.partner', string='Customer', tracking=2)
    phone = fields.Char('Phone')
    email = fields.Char('Email')
    
    request_date = fields.Date('Request Date', default=lambda self:datetime.now().date(), tracking=1)
    close_date = fields.Date('Close Date', tracking=3)
    duration = fields.Float('Repairing Duration(In Hours)', compute='_get_duration')
    project_id = fields.Many2one('project.project', string='Project')
    product_id = fields.Many2one('fleet.vehicle.model', string='Vehicle Model')
    machine_name = fields.Char('Vehicle Name')
    brand = fields.Char('Brand')
    model = fields.Char('Model')
    machine_year = fields.Char('Manufacturing Year')
    vehicle_meter = fields.Float('Meter Reading')
    vehicle_number = fields.Char('Number Plate')
    demage = fields.Text('Damage')
    
    team_id = fields.Many2one('crm.team', tracking=2, default=_get_default_team)
    user_id = fields.Many2one('res.users', string='Technician', tracking=2,domain=[('share','=',False)])
    company_id = fields.Many2one('res.company', default=lambda self:self.env.company)
    priority = fields.Selection([('0','Low'),('1','Normal'),('2','High'),('3','Very High')], default="1", string='Priority')
    service_id = fields.Many2one('dev.machine.service', string='Service')
    service_type_id = fields.Many2one('fleet.service.type', string='Service Type')
    state = fields.Selection([('draft','Draft'),('assign','Assign'),('confirm','Confirm'),('in_progress','In Process'),('done','Done'),('cancel','Cancel')], default='draft', string='Status', tracking=2, copy=False)
    
    notes = fields.Text('Description')
    product_lines = fields.One2many('dev.repair.request.product.lines','repair_request_id', string='Product Lines')
    service_product_lines = fields.One2many('service.product.lines','repair_request_id', string='Service Product Lines')
    diagnosys_id = fields.Many2one('project.task', string='Diagnosys', copy=False)
    workorder_id = fields.Many2one('project.task', string='Work Order', copy=False)
    timesheet_lines = fields.One2many('account.analytic.line','repair_request_id', string='Timesheet Lines')
    is_repair = fields.Boolean('Repair Vehicle')
    sale_count = fields.Integer('Sale', related='diagnosys_id.sale_count')
    document_ids = fields.One2many('ir.attachment','res_id', string='Repair Documents')
    doc_count = fields.Integer(compute='_compute_document_count', string='Documents Count')
    instruction_lines = fields.One2many('repair.checklist.lines','repair_id', string='Instruction Lines')
    # lead_counter = fields.Integer(string='Repair Request ', compute='lead_count')
    calender_id = fields.Many2one('calendar.event', string='Event', copy=False)
    inspection_template_id = fields.Many2one('inspection.template', string='Inspection Template', copy=False)
    calendar_event_id = fields.Many2one('calendar.event',string="Calendar Event")
    
    

    # def action_view_lead(self):
    #     lead_ids = self.env['crm.lead'].search([('id', '=', self.lead_id.id)])
    #     list_id = lead_ids.ids
    #     action = self.env.ref('crm.crm_lead_action_pipeline').sudo().read()[0]
    #     if len(list_id) > 1:
    #         action['domain'] = [('id', 'in', list_id)]
    #     elif len(list_id) == 1:
    #         action['views'] = [(self.env.ref('crm.crm_lead_view_form').id, 'form')]
    #         action['res_id'] = list_id[0]
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     return action

    # def lead_count(self):
    #     for rec in self:
    #         lead_ids = self.env['crm.lead'].search([('id', '=', self.lead_id.id)])
    #         list_id = lead_ids.ids
    #         counter = len(list_id)
    #     rec.lead_counter = counter
    
    
    def service_renew_cron(self):
        date = fields.Date.today()
        month = self.env.company.month_duration
        template_id = self.env.ref('dev_garage_management.customer_service_renew_garage_template')
        repair_request_ids = self.env['dev.repair.request'].search([('state','=','done')])
        for repair in repair_request_ids:
            if month >= 4:
                compare_date = repair.request_date + relativedelta(months=month)
                if compare_date == date:
                    if template_id:
                          template_id.send_mail(repair.id, True)
    
    
    @api.depends()
    def _compute_document_count(self):
        for repair in self:
            repair.doc_count = len(repair.document_ids)
    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'dev.repair.request'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'dev.repair.request', 'default_res_id': self.id}
        res['name'] = 'Images'
        return res
    
    def get_priority(self):
        priority = int(self.priority)
        lst = []
        for p in range(0, priority):
            lst.append(p)
        return lst
        
    
    def action_view_sale_order(self):
        return self.diagnosys_id.action_view_sale_order()
    
    @api.depends('timesheet_lines','timesheet_lines.unit_amount')
    def _get_duration(self):
        for request in self:
            hour = 0
            for timesheet in request.timesheet_lines:
                hour += timesheet.unit_amount
            request.duration = hour
    
    @api.onchange('product_id')
    def onchange_machine(self):
        if self.product_id:
            self.machine_name = self.product_id.name
        #    self.vehicle_number = self.product_id.license_plate
        #    self.vehicle_meter = self.product_id.odometer
        #    self.model = self.product_id.model_id.name
            self.brand = self.product_id.brand_id.name
            
    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({
                'name': self.env['ir.sequence'].next_by_code('dev.repair.request') or '/'
            })
        requests = super(repair_request, self).create(vals_list)

        for request in requests:
            if request.customer_id and request.customer_id not in request.message_partner_ids:
                request.message_subscribe([request.customer_id.id])

        return requests            
#    @api.model
#    def create(self,vals):
#        vals.update({
#                    'name':self.env['ir.sequence'].next_by_code('dev.repair.request') or '/'
#                })
#        request = super(repair_request, self).create(vals)
#        if request.customer_id not in request.message_partner_ids:
#            request.message_subscribe([request.customer_id.id])
#        return request
    
    def unlink(self):
        for request in self:
            if request.state not in ['draft','cancel']:
                raise ValidationError(_('Job Card delete on Draft and cancel state only !!!.'))
        return super(repair_request, self).unlink()
        
    @api.onchange('customer_id')
    def onchange_customer(self):
        if self.customer_id:
            self.phone = self.customer_id.phone
            self.email = self.customer_id.email
        else:
            self.phone = ''
            self.email = ''
    
    
    def action_assign_request(self):
        if not self.user_id or not self.team_id:
            raise ValidationError(_('Please Assign team and technician to Job Card.'))
        self.state ='assign'
        

    def action_confirm_request(self):
        if not self.project_id:
            raise ValidationError(_('Please Select Project.'))
        if not self.close_date:
            raise ValidationError(_('Please Assign Close Date to Job Card.'))
        self.state = 'confirm'  
    
    def action_process_request(self):
        self.state = 'in_progress'
    
    def action_cance_request(self):
        if self.timesheet_lines:
            self.timesheet_lines.unlink()
        if self.diagnosys_id:
            if self.diagnosys_id:
                self.diagnosys_id.sale_id.action_cancel()
                self.diagnosys_id.sale_id.unlink()
            self.diagnosys_id.unlink()
        if self.workorder_id:
            self.workorder_id.unlink()
            
        self.state = 'cancel'
    
    def action_set_draft_request(self):
        self.state = 'draft'
        
    def action_done_request(self):
        if not self.workorder_id:
            raise ValidationError(_('Please Create Workorder for Job Card.'))
        if not self.diagnosys_id:
            raise ValidationError(_('Please Create Diagnosis for Job Card.'))
        if not self.timesheet_lines:
            raise ValidationError(_('Plese Add timesheet in workorder.'))
        template_id = self.env.ref('dev_garage_management.customer_email_template_garage_job_closed')
        self.state = 'done'
        for record in self:
            if template_id and record.customer_id.email:
                template_id.send_mail(record.id, True)
        
    
    def action_create_diagnostic(self):
        if not self.project_id:
            raise ValidationError(_("Please Select Project."))
        if not self.user_id:
            raise ValidationError(_('Please Select Technician.'))
        if not self.close_date:
            raise ValidationError(_('Please Select Close Date.'))
        if not self.service_product_lines:
            raise ValidationError(_('Please Add Service Charge.'))
        vals={
            'project_id':self.project_id and self.project_id.id or False,
            'name':self.desc +' [ ' + self.name + ' ]',
            'user_ids':self.user_id and self.user_id.ids or False,
            'partner_id':self.customer_id and self.customer_id.id or False,
            'date_deadline':self.close_date or False,
            'repair_request_id':self.id,
            'task_type':'diagnosys',
            'description':self.notes,
            'product_lines': [(0,0,{'product_id': line.product_id.id, 
                                    'name': line.name,
                                    'quantity': line.quantity,
                                    'uom_id': line.uom_id.id,
                                    'price': line.price,
                                    }) for line in self.service_product_lines],
              }
        task_id = self.env['project.task'].sudo().create(vals)
        if task_id:
            self.diagnosys_id = task_id and task_id.id or False
    
    def action_create_workorder(self):
        if not self.project_id:
            raise ValidationError(_("Please Select Project."))
        if not self.user_id:
            raise ValidationError(_('Please Select Technician.'))
        if not self.close_date:
            raise ValidationError(_('Please Select Close Date.'))
        vals={
            'project_id':self.project_id and self.project_id.id or False,
            'name':self.desc +' [ ' + self.name + ' ]',
            'user_ids':self.user_id and self.user_id.ids or False,
            'partner_id':self.customer_id and self.customer_id.id or False,
            'date_deadline':self.close_date or False,
            'repair_request_id':self.id,
            'task_type':'work_order',
            'description':self.notes,
        }
        task_id = self.env['project.task'].sudo().create(vals)
        if task_id:
            self.workorder_id = task_id and task_id.id or False
    
    def view_machine_diagnosys(self):
        ctx = dict(create=False)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Diagnosis',
            'res_model': 'project.task',
            'domain': [('id', '=', self.diagnosys_id.id)],
            'view_mode': 'list,form',
            'target': 'current',
            'context': ctx,
        }
    
    def view_machine_workorder(self):
        ctx = dict(create=False)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Workorder',
            'res_model': 'project.task',
            'domain': [('id', '=', self.workorder_id.id)],
            'view_mode': 'list,form',
            'target': 'current',
            'context': ctx,
        }
    
    def get_selection_label(self, object, field_name, field_value):
        return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])
    
        
    def load_inspection(self):
        if self.instruction_lines:
            self.instruction_lines.unlink()
            
        if not self.inspection_template_id:
            raise ValidationError(_("Please select Inspection Template")) 
            
        for rec in self.inspection_template_id.inspection_ids:                                                         
            self.instruction_lines = [(0,0,
                                       { 'instruction_id':rec.id, 
                                         'repair_id' : self.id,
                                        }
                                    )]  
        

class repair_checklist_lines(models.Model):
    _name ='repair.checklist.lines'
    _description = 'Repair Checklist Lines'
    
    instruction_id = fields.Many2one('dev.machine.instruction', string='Inspection')
    is_check = fields.Boolean('Checked')
    repair_id = fields.Many2one('dev.repair.request', string='Reapir')
    
    def action_check(self):
        self.is_check = True              
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
