# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class repair_request_lead(models.Model):
    _inherit = 'crm.lead'
    
    product_id = fields.Many2one('fleet.vehicle.model', string='Vehicle Model')
    machine_name = fields.Char('Vehicle Name')
    demage = fields.Text('Damage')
    service_id = fields.Many2one('dev.machine.service', string='Service')
    service_type_id = fields.Many2one('fleet.service.type', string='Service Type')
    repair_issue = fields.Char('Repair Issue')
    repair_reason = fields.Char('Reason For Repair')
    job_card = fields.Integer(string='Job Card ', compute='job_card_count')
    
    
    @api.onchange('product_id')
    def onchange_machine(self):
        if self.product_id:
            self.machine_name = self.product_id.name
            
            
    def action_create_job_card(self):
        vals = {'desc': self.name,
                'customer_id': self.partner_id.id,
                'priority': self.priority,
                'email': self.email_from,
                'phone': self.phone,
                'product_id': self.product_id.id,
                'machine_name': self.machine_name,
                'demage': self.demage,
                'service_id': self.service_id.id,
                'service_type_id': self.service_type_id.id,
                'team_id': self.team_id.id,
                'notes': self.repair_issue + "\n" + self.repair_reason,
                'lead_id': self.id
                }
        job_card = self.env['dev.repair.request'].create(vals)
        job_card.onchange_machine()
        
    def action_job_card(self):
        job_card_ids = self.env['dev.repair.request'].search([('lead_id', '=', self.id)])
        list_id = job_card_ids.ids
        action = self.env.ref('dev_garage_management.action_machine_repair_request').sudo().read()[0]
        if len(list_id) > 1:
            action['domain'] = [('id', 'in', list_id)]
        elif len(list_id) == 1:
            action['views'] = [(self.env.ref('dev_garage_management.view_dev_repair_request_form').id, 'form')]
            action['res_id'] = list_id[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def job_card_count(self):
        for rec in self:
            job_card_ids = self.env['dev.repair.request'].search([('lead_id', '=', self.id)])
            list_id = job_card_ids.ids
            counter = len(list_id)
        self.job_card = counter

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
