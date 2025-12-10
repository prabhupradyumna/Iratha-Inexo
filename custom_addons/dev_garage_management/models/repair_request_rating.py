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
from datetime import datetime
from odoo.exceptions import ValidationError
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta


class repair_request_rating(models.Model):
    _name = "dev.repair.request"
    _inherit = ['rating.mixin','dev.repair.request']
    
    
     #  ======= Rating Value ====================
    def _get_rating_value(self):
        for rec in self:
            feedback_rate = False
            feedback_date = False
            rating_image = False
            review = ''
            rating_text = False
            rating_id = rec.env['rating.rating'].search([('res_id', '=', rec.id), ('res_model', '=', 'dev.repair.request')],
                                                        order='id desc', limit=1)
            if rating_id:
                rating = int(rating_id.rating)
                if rating > 4:
                    rating = 4
                feedback_rate = str(rating)
                feedback_date = rating_id.write_date
                rating_image = rating_id.rating_image
                review = rating_id.feedback
                rating_text = rating_id.rating_text
            rec.feedback_rate = feedback_rate
            rec.feedback_date = feedback_date
            rec.rating_image = rating_image
            rec.review = review
            rec.rating_text = rating_text

    def send_rating_email(self):
        template_id = self.env.ref('dev_garage_management.rating_service_request_email_template')
        if template_id:
            self.rating_send_request(template_id, lang=self.customer_id.lang, force_send=True)

    feedback_rate = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')],
                                     default='0', string='Rate', compute='_get_rating_value', readonly=True)
    feedback_date = fields.Date('Feedback Date', compute='_get_rating_value', readonly=True)
    review = fields.Text('Review', compute='_get_rating_value', readonly=True)
    rating_image = fields.Binary('Image', compute='_get_rating_value', readonly=True)
    rating_text = fields.Selection([
        ('top', 'Satisfied'),
        ('ok', 'Okay'),
        ('ko', 'Dissatisfied'),
        ('none', 'No Rating yet')], string='Rating', readonly=True)
    
    
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
