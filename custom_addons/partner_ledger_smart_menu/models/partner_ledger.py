from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    ledger_balance = fields.Monetary(
        string='Ledger Balance',
        compute='_compute_ledger_balance',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', readonly=True
    )

    def _compute_ledger_balance(self):
        for partner in self:
            # Only posted move lines linked to the partner’s receivable/payable accounts
            lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('move_id.state', '=', 'posted'),
                ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
            ])

            debit = sum(lines.mapped('debit'))
            credit = sum(lines.mapped('credit'))

            # Net position (positive = receivable, negative = payable)
            partner.ledger_balance = debit - credit

    def action_open_ledger_wizard(self):
        """Opens the date-range wizard for ledger report."""
        self.ensure_one()
        return {
            'name': f'{self.name} Ledger Report',
            'type': 'ir.actions.act_window',
            'res_model': 'partner.ledger.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id},
        }
