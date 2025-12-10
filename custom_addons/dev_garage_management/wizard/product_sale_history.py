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
from datetime import date,datetime
from odoo.exceptions import ValidationError

class product_sale_history(models.TransientModel):
    _name = 'product.sale.history'
    _description = 'Job Card History'
    
    start_date = fields.Date(string='Start Date',default=fields.Date.today(), required=True)
    end_date = fields.Date(string='End Date', required=True)
    
    @api.onchange('end_date','start_date')  
    def onchange_of_end_date(self):
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                    raise ValidationError(_("End date must be greater than the start date."))

    def print_product_sale_history_report(self):
        return self.env.ref('dev_garage_management.dev_product_sale_history_report_menu').report_action(self)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
