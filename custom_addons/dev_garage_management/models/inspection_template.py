# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields,api

class inspection_template(models.Model):
    _name = 'inspection.template'
    _description='Inspection Template'
    
    name=fields.Char(string='Name', required='True')
    inspection_ids=fields.Many2many('dev.machine.instruction',string='Inspection')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
