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

class report_job_card(models.AbstractModel): 
    _name = 'report.dev_garage_management.product_sale_report_template'
    _description = 'Product Sale History Report'
         
        
    def product_sale_history(self, obj):
        product_quantities = {}  # Dictionary to store product quantities
        repair_request_ids = self.env['dev.repair.request'].search([
            ('request_date', '>=', obj.start_date),
            ('request_date', '<=', obj.end_date)
        ])
        for request in repair_request_ids:
            if request.diagnosys_id.sale_id:
                for product in request.diagnosys_id.sale_id.order_line:
                    product_name = product.product_id.name
                    product_qty = product.product_uom_qty 
                    product_quantities[product_name] = product_quantities.get(product_name, 0) + product_qty
        result = [{'product': key, 'quantity': value} for key, value in product_quantities.items()]
        print("===========", result)
        return result

         
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
