# from odoo import models, fields, api


# class partner_ledger(models.Model):
#     _name = 'partner_ledger.partner_ledger'
#     _description = 'partner_ledger.partner_ledger'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

