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


class crm_team(models.Model):
    _inherit = "crm.team"
    
    is_default = fields.Boolean('By Default')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
