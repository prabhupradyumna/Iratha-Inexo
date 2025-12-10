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


class product_template(models.Model):
    _inherit = "product.template"
    
    is_machine = fields.Boolean('Vehicle')
    is_machine_part = fields.Boolean('Vehicle Part')
    repair_count = fields.Integer('Repair Count', compute='_get_repair_count') 
    
    def _get_repair_count(self):
        for template in self:
            product_ids = self.env['product.product'].search([('product_tmpl_id','=',template.id)])
            count = 0
            for product in product_ids:
                repair_ids = self.env['dev.repair.request'].sudo().search([('product_id','=',product.id),
                                                                           ('state','!=','cancel')])
                count += len(repair_ids)
            template.repair_count = count 
    
    def get_repair_ids(self):
        product_ids = self.env['product.product'].search([('product_tmpl_id','=',self.id)])
        rep_ids = []
        for product in product_ids:
            repair_ids = self.env['dev.repair.request'].sudo().search([('product_id','=',product.id),
                                                                           ('state','!=','cancel')])
            for rep in repair_ids:
                rep_ids.append(rep.id)
        return rep_ids
    
    def action_view_repaire_request(self):
        repair_ids = self.get_repair_ids()
        action = self.env["ir.actions.actions"]._for_xml_id("dev_garage_management.action_machine_repair_request")
        if len(repair_ids) > 1:
            action['domain'] = [('id', 'in', repair_ids)]
        elif len(repair_ids) == 1:
            form_view = [(self.env.ref('dev_garage_management.view_dev_repair_request_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = repair_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'create': 0,
        }
        action['context'] = context
        return action
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
