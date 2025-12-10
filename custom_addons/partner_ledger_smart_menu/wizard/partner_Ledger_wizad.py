from odoo import models, fields, api
from datetime import date


class PartnerLedgerWizard(models.TransientModel):
    _name = 'partner.ledger.wizard'
    _description = 'Partner Ledger Wizard'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, readonly=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.model
    def default_get(self, fields):
        """Prefill partner and date defaults."""
        res = super().default_get(fields)
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')

        if active_model == 'res.partner' and active_id:
            res['partner_id'] = active_id

            first_line = self.env['account.move.line'].search([
                ('partner_id', '=', active_id),
                ('move_id.state', '=', 'posted'),
                ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
            ], order='date asc', limit=1)

            res['start_date'] = first_line.date if first_line else date.today()
            res['end_date'] = date.today()

        res['company_id'] = self.env.company.id
        return res

    def _get_opening_balance(self):
        """Compute opening balance before the start date."""
        self.ensure_one()
        self.env.cr.execute("""
            SELECT COALESCE(SUM(debit) - SUM(credit), 0)
            FROM account_move_line
            WHERE partner_id = %s
              AND date < %s
              AND move_id IN (SELECT id FROM account_move WHERE state = 'posted')
              AND account_id IN (
                SELECT id FROM account_account
                WHERE account_type IN ('asset_receivable', 'liability_payable')
              )
        """, (self.partner_id.id, self.start_date))
        return self.env.cr.fetchone()[0] or 0.0

    def get_ledger_lines(self):
        """Return ledger data including totals."""
        self.ensure_one()
        opening_balance = self._get_opening_balance()
        balance = opening_balance
        total_debit = 0.0
        total_credit = 0.0
        ledger_lines = []

        # Opening balance row
        ledger_lines.append({
            'date': '',
            'voucher_no': '',
            'type': 'Opening Balance',
            'debit': 0.0,
            'credit': 0.0,
            'balance': balance,
        })

        # Fetch all partner move lines in the period
        lines = self.env['account.move.line'].search([
            ('partner_id', '=', self.partner_id.id),
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
            ('move_id.state', '=', 'posted'),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
        ], order='date asc')

        for line in lines:
            debit = line.debit or 0.0
            credit = line.credit or 0.0
            total_debit += debit
            total_credit += credit
            balance += debit - credit

            move = line.move_id
            journal = move.journal_id
            account = line.account_id

            # Default type mapping
            display_type = {
                'out_invoice': 'Sale',
                'in_invoice': 'Purchase',
                'out_refund': 'Credit Note',
                'in_refund': 'Debit Note',
            }.get(move.move_type, 'Journal Entry')

            # --- Opening Balance Detection ---
            if any(word in (account.name or '').lower() for word in ['opening', 'retained', 'balance']) \
                    or '999999' in (account.code or '') \
                    or 'opening' in (journal.name or '').lower() \
                    or (journal.code and journal.code.upper() == 'OPN'):
                display_type = 'Opening Balance'

            # --- Receipt Detection (based on journal type) ---
            elif move.move_type == 'entry' and journal.type in ('bank', 'cash'):
                display_type = 'Receipt'

            ledger_lines.append({
                'date': line.date.strftime('%d-%m-%Y'),
                'voucher_no': move.name or '',
                'type': display_type,
                'debit': debit,
                'credit': credit,
                'balance': balance,
            })

        # Totals
        ledger_lines.append({
            'date': '',
            'voucher_no': '',
            'type': 'Total',
            'debit': total_debit,
            'credit': total_credit,
            'balance': balance,
        })

        return ledger_lines

    def action_print_html(self):
        """Generate the HTML report."""
        self.ensure_one()
        report = self.env.ref('partner_ledger.report_partner_ledger')
        return report.report_action(self)
