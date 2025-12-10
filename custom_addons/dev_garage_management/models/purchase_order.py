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


class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    project_task_id = fields.Many2one('project.task', string='Project Task')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
