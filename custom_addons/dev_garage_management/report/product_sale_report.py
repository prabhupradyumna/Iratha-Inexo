# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api
from num2words import num2words

class report_product_sale(models.AbstractModel): 
    _name = 'report.dev_garage_management.product_sale_report_template'
   
    def product_sale_history(self, obj):
         product_sale_ids=self.env['dev.repair.request'].search([('request_date','>=',obj.start_date),('request_date','<=',obj.end_date)])
         return product_sale_ids
         
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['product.sale.history'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'product.sale.history',
            'docs': docs,
            'product_sale_history':self.product_sale_history,
          }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
