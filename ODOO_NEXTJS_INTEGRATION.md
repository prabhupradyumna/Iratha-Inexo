# Odoo 19 + Next.js Integration Guide

This document outlines the implementation of authentication between your Next.js frontend and Odoo 19 backend.

## ✅ Completed Steps

### Step 2: Next.js RPC Client Utility ✅

**File:** `src/lib/odoo-client.ts`

This utility provides a `callOdoo()` function that:
- Communicates with Odoo using JSON-RPC 2.0 protocol
- Handles session cookie management
- Supports both authenticated and public endpoints
- Uses environment variable `ODOO_BASE_URL` (defaults to `http://localhost:8069`)

**Usage Example:**
```typescript
import { callOdoo } from '@/lib/odoo-client';

const response = await callOdoo({
  endpoint: '/web/session/authenticate',
  params: { db: 'mydb', login: 'admin', password: 'admin' }
});
```

### Step 3: Authentication Server Action ✅

**File:** `src/actions/auth.ts`

This module provides three server actions:

1. **`login(formData: FormData)`** - Authenticates user with Odoo
   - Extracts `db`, `login`, and `password` from form data
   - Calls Odoo's `/web/session/authenticate` endpoint
   - Stores session ID in secure HTTP-only cookie
   - Redirects to `/dashboard` on success

2. **`logout()`** - Clears session and redirects to sign-in

3. **`getSession()`** - Checks authentication status

**Usage Example:**
```typescript
import { login } from '@/actions/auth';

// In a Server Component or Server Action
const formData = new FormData();
formData.append('db', 'mydb');
formData.append('login', 'admin');
formData.append('password', 'admin');
const result = await login(formData);
```

### Step 1: Odoo Backend Module ✅

**Location:** `odoo-19.0/custom_addons/nextjs_connector/`

**Module Structure:**
```
nextjs_connector/
├── __init__.py
├── __manifest__.py
├── README.md
└── controllers/
    ├── __init__.py
    └── main.py
```

**Features:**
- Health check endpoint at `/api/health` (public, JSON-RPC)
- Ready for future API endpoints
- Follows Odoo module best practices

## 📋 Next Steps

### 1. Install the Odoo Module

1. **Restart Odoo** to detect the new module:
   ```bash
   cd odoo-19.0
   ./odoo-bin -c odoo.conf --update=nextjs_connector
   ```

2. **Install via Odoo UI:**
   - Go to Apps menu
   - Remove "Apps" filter
   - Search for "Next.js Connector"
   - Click Install

3. **Verify installation:**
   ```bash
   curl -X POST http://localhost:8069/api/health \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "call", "params": {}, "id": 1}'
   ```

### 2. Configure Environment Variables

Create a `.env.local` file in your Next.js project root:

```env
# Odoo Backend Configuration
ODOO_BASE_URL=http://localhost:8069
```

**Note:** Your `odoo.conf` shows `xmlrpc_port = 6066`, but the web interface typically runs on port 8069. If your Odoo web interface runs on a different port, update `ODOO_BASE_URL` accordingly.

### 3. Update Sign-In Form (Step 4)

You'll need to update `src/components/Auth/SigninWithPassword.tsx` to:
- Add a database field (or use a default)
- Use the `login` Server Action instead of the current mock implementation
- Handle loading states and error messages

**Example update:**
```typescript
"use client";
import { login } from "@/actions/auth";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SigninWithPassword() {
  const router = useRouter();
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(formData: FormData) {
    setLoading(true);
    setError("");
    
    const result = await login(formData);
    
    if (!result.success) {
      setError(result.error || "Login failed");
      setLoading(false);
    }
    // On success, login() will redirect automatically
  }

  return (
    <form action={handleSubmit}>
      {/* Add database field */}
      <input name="db" defaultValue="your_database_name" />
      {/* ... rest of form fields ... */}
      {error && <div className="text-red-500">{error}</div>}
    </form>
  );
}
```

### 4. Create Protected Dashboard Route (Step 5)

Create `src/app/dashboard/page.tsx`:

```typescript
import { getSession } from "@/actions/auth";
import { redirect } from "next/navigation";

export default async function Dashboard() {
  const session = await getSession();
  
  if (!session.authenticated) {
    redirect("/auth/sign-in");
  }

  return (
    <div>
      <h1>Welcome to Admin Dashboard</h1>
      <p>Logged in as: {session.username}</p>
    </div>
  );
}
```

## 🔧 Testing the Integration

1. **Test Health Endpoint:**
   ```bash
   curl -X POST http://localhost:8069/api/health \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "call", "params": {}, "id": 1}'
   ```

2. **Test Authentication:**
   - Start your Next.js dev server: `npm run dev`
   - Navigate to `/auth/sign-in`
   - Enter your Odoo database name, login, and password
   - Submit the form
   - Should redirect to `/dashboard` on success

## 📝 Important Notes

1. **Database Name:** You'll need to know your Odoo database name. Common defaults are the database name you created during Odoo setup.

2. **CORS:** Since we're using Server Actions, CORS is not an issue. All requests go through Next.js server.

3. **Session Management:** The session ID is stored in an HTTP-only cookie, making it secure from XSS attacks.

4. **Port Configuration:** 
   - Your `odoo.conf` shows `xmlrpc_port = 6066`
   - The web interface typically runs on port 8069
   - Verify which port your Odoo web interface uses and update `ODOO_BASE_URL` accordingly

5. **Security:** In production, ensure:
   - `ODOO_BASE_URL` uses HTTPS
   - Cookies are set with `secure: true` (already handled in code)
   - Consider adding rate limiting for login attempts

## 🐛 Troubleshooting

**Issue:** "Connection refused" or "Failed to call Odoo"
- Verify Odoo is running: `http://localhost:8069`
- Check `ODOO_BASE_URL` in `.env.local`
- Ensure firewall allows connections

**Issue:** "Invalid credentials" but credentials are correct
- Verify database name is correct
- Check Odoo logs for authentication errors
- Ensure user exists in the specified database

**Issue:** Module not appearing in Odoo Apps
- Verify `custom_addons` is in `addons_path` in `odoo.conf`
- Restart Odoo with `--update=all` flag
- Check Odoo logs for module loading errors

## 📚 File Structure Summary

```
Project Root/
├── src/
│   ├── actions/
│   │   └── auth.ts                    # Server Actions (Step 3) ✅
│   ├── lib/
│   │   └── odoo-client.ts             # RPC Helper (Step 2) ✅
│   └── app/
│       ├── auth/
│       │   └── sign-in/
│       │       └── page.tsx           # Sign-in page (needs update)
│       └── dashboard/
│           └── page.tsx                # Dashboard (needs creation)
└── odoo-19.0/
    └── custom_addons/
        └── nextjs_connector/           # Odoo Module (Step 1) ✅
            ├── __init__.py
            ├── __manifest__.py
            ├── README.md
            └── controllers/
                ├── __init__.py
                └── main.py
```

## ✅ Checklist

- [x] Step 1: Odoo module structure created
- [x] Step 2: RPC client utility created
- [x] Step 3: Authentication Server Action created
- [ ] Step 4: Update sign-in form to use Server Action
- [ ] Step 5: Create protected dashboard route
- [ ] Install Odoo module
- [ ] Configure environment variables
- [ ] Test authentication flow

