# in my_gas_agency/models/gas_agency_payment.py
from odoo import models, fields


class GasAgencyPayment(models.Model):
    """
    This model stores a single "Credit" transaction for a commercial customer.
    This represents a payment received.
    """
    _name = 'gas.agency.payment'
    _description = 'Gas Agency Customer Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: 'New'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True,
        domain="[('is_commercial_customer', '=', True)]"
    )
    date = fields.Date(
        string="Payment Date",
        required=True,
        default=fields.Date.context_today
    )
    amount = fields.Float(
        string="Credit Amount",
        help="The total amount received from the customer."
    )
    journal = fields.Selection(
        [('bank', 'Bank'), ('cash', 'Cash')],
        string="Journal",
        default='bank',
        required=True
    )

    # This is for creating the payment reference
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('gas.agency.payment') or 'New'
        return super(GasAgencyPayment, self).create(vals)