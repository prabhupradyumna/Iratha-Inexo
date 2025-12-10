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


class account_analytic_line(models.Model):
    _inherit = "account.analytic.line"
    
    repair_request_id = fields.Many2one('dev.repair.request', string='Repair Request')
    
    
    @api.onchange('project_id')
    def onchange_project(self):
        if self.project_id:
            self.account_id = self.project_id.auto_account_id and self.project_id.auto_account_id.id or False
        else:
            self.account_id = False
            
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
