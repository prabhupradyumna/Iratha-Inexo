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


class dev_machine_instruction(models.Model):
    _name = "dev.machine.instruction"
    _description = "Machine Instruction"
    
    name = fields.Char('Name', required="1")
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
