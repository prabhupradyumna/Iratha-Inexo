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
    _name = 'report.dev_garage_management.job_card_history_report_template'
    _description = 'Job Card History Report'
   
    def job_card_history(self, obj):
         job_card_ids=self.env['dev.repair.request'].search([('request_date','>=',obj.start_date),('request_date','<=',obj.end_date)])
         return job_card_ids
         
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['job.card.history'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'job.card.history',
            'docs': docs,
            'job_card_history':self.job_card_history,
          }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
