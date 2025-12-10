# in my_gas_agency/models/gas_agency_ledger.py
from odoo import models, fields, api, tools  # <-- Import tools


class GasAgencyLedger(models.Model):
    """
    A read-only 'virtual' model to display the combined partner ledger.
    This model does not create a database table (_auto = False).
    It is populated by a custom SQL query.
    """
    _name = 'gas.agency.ledger'
    _description = 'Gas Agency Partner Ledger'
    _auto = False
    _order = 'date desc, id desc'

    # --- Fields for our Ledger View ---
    partner_id = fields.Many2one('res.partner', string="Customer", readonly=True)
    date = fields.Date(string="Date", readonly=True)
    particulars = fields.Char(string="Particulars", readonly=True)
    filled_qty = fields.Integer(string="Filled", readonly=True)
    empty_qty = fields.Integer(string="Empty", readonly=True)
    debit = fields.Float(string="Debit", readonly=True)
    credit = fields.Float(string="Credit", readonly=True)
    reference_model = fields.Char(string="Ref Model", readonly=True)
    reference_id = fields.Integer(string="Ref ID", readonly=True)

    @api.model
    def init(self):
        """
        This is the core logic. We create a PostgreSQL VIEW
        that unions the Debits (Invoices) and Credits (Payments).
        """
        # Use standard 'tools.drop_view_if_exists' and self._table
        tools.drop_view_if_exists(self.env.cr, self._table)

        sql_debits = """
            SELECT
                am.id as id,
                am.partner_id as partner_id,
                am.date as date,
                am.name as particulars,
                'account.move' as reference_model,
                am.id as reference_id,
                am.amount_total as debit,
                0.0 as credit,
                COALESCE(SUM(CASE WHEN pt.name::text ILIKE '%%(Filled)%%' THEN aml.quantity ELSE 0 END), 0) as filled_qty,
                COALESCE(SUM(CASE WHEN pt.name::text ILIKE '%%(Empty)%%' THEN aml.quantity ELSE 0 END), 0) as empty_qty
            FROM
                account_move am
            JOIN 
                res_partner rp ON am.partner_id = rp.id
            -- Use LEFT JOINs to ensure invoices show up even with no lines
            LEFT JOIN
                account_move_line aml ON aml.move_id = am.id
            LEFT JOIN
                product_product pp ON aml.product_id = pp.id
            LEFT JOIN
                product_template pt ON pp.product_tmpl_id = pt.id
            WHERE
                rp.is_commercial_customer = TRUE
                AND am.move_type = 'out_invoice'
                AND am.state = 'posted'
            GROUP BY
                am.id, am.partner_id, am.date, am.name, am.amount_total
        """

        sql_credits = """
            SELECT
                (gap.id + 10000000) as id,
                gap.partner_id as partner_id,
                gap.date as date,
                gap.name as particulars,
                'gas.agency.payment' as reference_model,
                gap.id as reference_id,
                0.0 as debit,
                gap.amount as credit,
                0 as filled_qty,
                0 as empty_qty
            FROM
                gas_agency_payment gap
            JOIN 
                res_partner rp ON gap.partner_id = rp.id
            WHERE
                rp.is_commercial_customer = TRUE
        """

        # Use self._table for the view name, it's safer
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                {sql_debits}
                UNION ALL
                {sql_credits}
            )
        """)