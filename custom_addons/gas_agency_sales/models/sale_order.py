# in gas_agency_sales/models/sale_order.py
from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """
        Override the 'Confirm' button to create the empty
        return lines automatically before confirming.
        """
        for order in self:
            new_lines_to_create = []

            # Loop over a copy [:] because we might create new lines
            for line in order.order_line[:]:
                # Check if this line has empty return data
                if line.x_empty_product_id and line.x_empty_qty > 0:
                    # Prepare the new "return" line's data
                    new_lines_to_create.append({
                        'order_id': order.id,
                        'product_id': line.x_empty_product_id.id,
                        # Must be a NEGATIVE quantity for a return
                        'product_uom_qty': -line.x_empty_qty,
                        'price_unit': 0.0,  # Empties have no price
                    })

            # Create all the new 'empty' lines at once
            if new_lines_to_create:
                self.env['sale.order.line'].create(new_lines_to_create)

        # Now, call the original 'action_confirm' method
        return super(SaleOrder, self).action_confirm()