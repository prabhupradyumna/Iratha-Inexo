# Next.js Connector Module

This Odoo module provides API endpoints for integrating Odoo 19 backend with a Next.js frontend application.

## Installation

1. **Ensure the module is in the correct location:**
   - The module should be in `custom_addons/nextjs_connector/`
   - Verify that `custom_addons` is in your `addons_path` in `odoo.conf`

2. **Update Odoo addons list:**
   ```bash
   # Restart Odoo with --update flag
   ./odoo-bin -c odoo.conf --update=nextjs_connector
   ```

3. **Install the module:**
   - Go to Odoo Apps menu
   - Remove the "Apps" filter
   - Search for "Next.js Connector"
   - Click Install

## API Endpoints

### Health Check

**Endpoint:** `/api/health`

**Method:** POST

**Authentication:** Public (no auth required)

**Purpose:** Verify connection between Next.js and Odoo

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {},
  "id": 1
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "ok",
    "message": "Next.js connector is working",
    "odoo_version": "19.0"
  },
  "id": 1
}
```

## Testing the Connection

You can test the health endpoint using curl:

```bash
curl -X POST http://localhost:8069/api/health \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {},
    "id": 1
  }'
```

## Notes

- This module uses Odoo's native `/web/session/authenticate` endpoint for authentication
- All endpoints use JSON-RPC 2.0 protocol for consistency
- The module is designed to be extended with additional endpoints as needed

