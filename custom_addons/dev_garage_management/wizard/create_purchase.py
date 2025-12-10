# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##########################################################################

from odoo import fields, models, api

class create_purchase(models.TransientModel):
    _name = 'create.purchase'
    _description = 'Create Purchase Order'
    
    
    def get_product(self):
        active_ids = self._context.get('active_ids')
        task = self.env['project.task'].browse(active_ids)
        product_lines = task.product_lines.mapped('product_id').filtered(lambda product: product.type != 'service')
        products = self.product_ids = [(6, 0, product_lines.ids)] if product_lines else False
        return products
        
    
    partner_id = fields.Many2one('res.partner', string='Vendor',required=True)
    product_ids = fields.Many2many('product.product',string="Products",default=get_product)
    
    def action_create_purchase_order(self):
        active_ids = self._context.get('active_ids')
        record = self.env['project.task'].browse(active_ids)
        if not record.product_lines:
            raise ValidationError(_('Please Add Estimation Lines.'))
        vals={
            'partner_id':self.partner_id and self.partner_id.id,
            'company_id':record.company_id and record.company_id.id or False,
          #  'user_id':record.user_id and record.user_id.id or False,
            'payment_term_id':self.partner_id and self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'project_task_id':record.id,
        }
        purchase_id = self.env['purchase.order'].sudo().create(vals)
        if purchase_id:
            line_val = []
            for line in self.product_ids:
                    line_val.append((0,0,{
                        'product_id':line.id or False,
                        'name':line.name or '',
                        'product_uom_qty': '1',
                        'product_uom_id':line.uom_id and line.uom_id.id or False,
                        'price_unit':line.standard_price,
                    }))
            purchase_id.order_line = line_val
            for line in purchase_id.order_line:
                line.onchange_product_id()
            record.purchase_id = purchase_id and purchase_id.id or False
            return record.action_view_purchase_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
