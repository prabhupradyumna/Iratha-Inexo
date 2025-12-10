# in gas_agency_sales/models/sale_order_line.py
from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # This is the "Empty Name" column
    x_empty_product_id = fields.Many2one(
        'product.product',
        string='Empty Product',
        domain="[('name', 'ilike', '(Empty)')]"
    )

    # This is the "Empty Qty" column
    x_empty_qty = fields.Integer(string='Empty Qty')