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


class service_product_lines(models.Model):
    _name = "service.product.lines"
    _description = "Service Product Lines"
    
    product_id = fields.Many2one('product.product', string='Product', required="1")
    name = fields.Text('Description', required="1")
    quantity = fields.Float('Quantity', default=1, required="1")
    uom_id = fields.Many2one('uom.uom', string='UOM')
    price = fields.Float('Price')
    repair_request_id  = fields.Many2one('dev.repair.request', string='Repair Request')
    
    
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.quantity = 1
            self.uom_id = self.product_id.uom_id and self.product_id.uom_id.id or False
            self.price = self.product_id.list_price or 0.0
        else:
            self.name = ''
            self.quantity = 0
            self.uom_id = False
            self.price = 0
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
