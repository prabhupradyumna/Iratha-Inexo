# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models


class instruction_checklist_report(models.AbstractModel):
    _name = 'report.dev_garage_management.machine_repair_card_report'
    _description='Instruction Checklist Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['dev.repair.request'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'dev.repair.request',
            'docs': docs,
        }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
