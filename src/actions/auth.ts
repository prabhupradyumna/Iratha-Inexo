/**
 * Authentication Server Actions
 * 
 * This module contains server-side actions for handling authentication
 * with the Odoo backend. These actions run on the server to avoid CORS
 * issues and keep credentials secure.
 */

"use server";

import { callOdoo } from "@/services/odoo-client";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

interface LoginResult {
  success: boolean;
  error?: string;
}

/**
 * Authenticates a user with Odoo backend
 * 
 * @param formData - Form data containing login credentials
 * @returns Promise with login result
 * 
 * @example
 * ```ts
 * const formData = new FormData();
 * formData.append('db', 'mydb');
 * formData.append('login', 'admin');
 * formData.append('password', 'admin');
 * const result = await login(formData);
 * ```
 */
export async function login(formData: FormData): Promise<LoginResult> {
  try {
    // Extract form data
    const db = formData.get("db") as string;
    const login = formData.get("login") as string;
    const password = formData.get("password") as string;

    // Validate required fields
    if (!db || !login || !password) {
      return {
        success: false,
        error: "Database, email, and password are required",
      };
    }

    // Call Odoo authentication endpoint
    const response = await callOdoo({
      endpoint: "/web/session/authenticate",
      params: {
        db,
        login,
        password,
      },
    });

    // Check if authentication was successful
    // Odoo returns user data on successful authentication
    if (response.result && typeof response.result === "object") {
      const result = response.result as Record<string, unknown>;
      
      // Odoo returns 'uid' (user ID) on successful login
      if (result.uid && typeof result.uid === "number") {
        // Store session ID in secure HTTP-only cookie
        if (response.sessionId) {
          const cookieStore = await cookies();
          cookieStore.set("odoo_session_id", response.sessionId, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            maxAge: 60 * 60 * 24 * 7, // 7 days
            path: "/",
          });

          // Also store user info for display in the UI (non-HTTP-only)
          const displayName = String(result.name || login);

          cookieStore.set("odoo_user_name", displayName, {
            httpOnly: false,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            maxAge: 60 * 60 * 24 * 7,
            path: "/",
          });

          cookieStore.set("odoo_user_email", login, {
            httpOnly: false,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            maxAge: 60 * 60 * 24 * 7,
            path: "/",
          });

          // Redirect to home dashboard on success
          redirect("/");
        } else {
          return {
            success: false,
            error: "Authentication succeeded but no session ID received",
          };
        }
      } else {
        return {
          success: false,
          error: "Invalid credentials",
        };
      }
    } else {
      return {
        success: false,
        error: "Invalid response from server",
      };
    }
  } catch (error) {
    // Handle errors gracefully
    const errorMessage =
      error instanceof Error ? error.message : "An unknown error occurred";
    
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Logs out the current user by clearing the session cookie
 * 
 * @returns Promise that resolves when logout is complete
 */
export async function logout(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete("odoo_session_id");
  cookieStore.delete("odoo_username");
  redirect("/auth/sign-in");
}

/**
 * Checks if the user is authenticated
 * 
 * @returns Promise with authentication status and user info
 */
export async function getSession(): Promise<{
  authenticated: boolean;
  name?: string;
  email?: string;
}> {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get("odoo_session_id");
  const name = cookieStore.get("odoo_user_name");
  const email = cookieStore.get("odoo_user_email");

  return {
    authenticated: !!sessionId?.value,
    name: name?.value,
    email: email?.value,
  };
}

