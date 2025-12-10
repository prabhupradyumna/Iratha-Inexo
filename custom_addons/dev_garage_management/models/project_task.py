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


class project_task(models.Model):
    _inherit = "project.task"
    
    task_type = fields.Selection([('diagnosys','Diagnosys'),('work_order','Work Order')], string='Type')
    repair_request_id = fields.Many2one('dev.repair.request', string='Repair Request')
    product_lines = fields.One2many('dev.repair.request.product.lines','task_id', string='Product Lines')
    sale_id = fields.Many2one('sale.order', string='Sales')
    purchase_id = fields.Many2one('purchase.order', string='Purchases')
    sale_count = fields.Integer('Sales Count', compute='get_sale_count')
    purchase_count = fields.Integer('Purchase Count', compute='get_purchase_count')
    
    
    def get_purchase_count(self):
        for task in self:
            purchase_ids = task.env['purchase.order'].search([('project_task_id', '=', task.id)])
            list_id = purchase_ids.ids
            counter = len(list_id)
        self.purchase_count = counter
        
    def action_view_all_purchase(self):
        purchase_ids = self.env['purchase.order'].search([('project_task_id', '=', self.id)])
        list_id = purchase_ids.ids
        action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        if len(list_id) > 1:
            action['domain'] = [('id', 'in', list_id)]
        elif len(list_id) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = list_id[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    @api.depends('sale_id')
    def get_sale_count(self):
        for task in self:
            if task.sale_id:
                task.sale_count = 1
            else:
                task.sale_count = 0
                
    def action_view_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        if self.sale_id:
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.sale_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'create': 0,
        }
        action['context'] = context
        return action
        
    
    def action_create_sale_order(self):
        if not self.product_lines:
            raise ValidationError(_('Please Add Estimation Lines.'))
        if not self.partner_id:
            raise ValidationError(_('Please Select Customer.'))
        vals={
            'partner_id':self.partner_id and self.partner_id.id,
            'pricelist_id':self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'company_id':self.company_id and self.company_id.id or False,
            'payment_term_id':self.partner_id and self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
        }
        sale_id = self.env['sale.order'].sudo().create(vals)
        if sale_id:
            line_val = []
            for line in self.product_lines:
                line_val.append((0,0,{
                    'product_id':line.product_id and line.product_id.id or False,
                    'name':line.name or '',
                    'product_uom_qty':line.quantity or 1,
                    'product_uom_id':line.uom_id and line.uom_id.id or False,
                    'price_unit':line.price,
                }))
            sale_id.order_line = line_val
            self.sale_id = sale_id and sale_id.id or False
            return self.action_view_sale_order()
            
    def action_view_purchase_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        if self.purchase_id:
            form_view = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.purchase_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'create': 0,
        }
        action['context'] = context
        return action
            
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
