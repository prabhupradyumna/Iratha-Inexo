# -*- coding: utf-8 -*-

"""
Next.js Connector Controller

This controller provides API endpoints for Next.js frontend integration.
All endpoints use JSON-RPC 2.0 protocol for consistency with Odoo's native API.
"""

from odoo import http
from odoo.http import request
import json


class NextJSConnector(http.Controller):
    """
    Main controller for Next.js integration endpoints
    """

    @http.route('/api/health', type='json', auth='public', methods=['POST'], csrf=False)
    def health_check(self, **kwargs):
        """
        Health check endpoint to verify connection between Next.js and Odoo
        
        Returns:
            dict: Status response indicating the connection is working
        
        Example JSON-RPC request:
        {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {},
            "id": 1
        }
        
        Example response:
        {
            "jsonrpc": "2.0",
            "result": {"status": "ok", "message": "Next.js connector is working"},
            "id": 1
        }
        """
        return {
            'status': 'ok',
            'message': 'Next.js connector is working',
            'odoo_version': request.env['ir.module.module'].sudo().search([
                ('name', '=', 'base')
            ]).latest_version or '19.0'
        }

