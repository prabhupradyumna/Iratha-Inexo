# in my_gas_agency/models/gas_agency_sale.py
from odoo import models, fields


class GasAgencySale(models.Model):
    """
    This model stores a single "Debit" transaction for a commercial customer.
    This represents a sale or delivery.
    """
    _name = 'gas.agency.sale'
    _description = 'Gas Agency Commercial Sale'
    _inherit = []  # For chatter
    _order = 'date desc, name desc'  # Show newest first

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
        domain="[('is_commercial_customer', '=', True)]"  # Only show commercial customers
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today
    )
    driver_name = fields.Char(string="Driver Name")  # From your requirements

    filled_qty = fields.Integer(string="Filled Qty")
    empty_qty = fields.Integer(string="Empty Qty")

    amount = fields.Float(
        string="Debit Amount",
        help="The total amount to be debited to the customer's ledger."
    )

    # This is for creating the "B No 27076" style reference
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('gas.agency.sale') or 'New'
        return super(GasAgencySale, self).create(vals)