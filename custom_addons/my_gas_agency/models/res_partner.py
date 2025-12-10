# in my_gas_agency/models/res_partner.py
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    is_commercial_customer = fields.Boolean(
        string="Is a Commercial Customer?",
        default=False,
        help="Check this box if this partner is a commercial credit customer."
    )

    def action_view_gas_agency_ledger(self):
        """Open the custom ledger view filtered for this partner."""
        self.ensure_one()
        return {
            'name': 'Partner Ledger',
            'type': 'ir.actions.act_window',
            'res_model': 'gas.agency.ledger',
            'view_mode': 'list',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
            },
            'target': 'current',
        }
