"use client";
import { EmailIcon, PasswordIcon } from "@/assets/icons";
import { login } from "@/actions/auth";
import Link from "next/link";
import React, { useState, useTransition } from "react";
import InputGroup from "../FormElements/InputGroup";
import { Checkbox } from "../FormElements/checkbox";

// Database icon component
function DatabaseIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 18 18"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M9 2.25C5.27208 2.25 2.25 3.27208 2.25 4.5V13.5C2.25 14.7279 5.27208 15.75 9 15.75C12.7279 15.75 15.75 14.7279 15.75 13.5V4.5C15.75 3.27208 12.7279 2.25 9 2.25Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M2.25 6.75C2.25 7.97792 5.27208 9 9 9C12.7279 9 15.75 7.97792 15.75 6.75"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M2.25 10.125C2.25 11.3529 5.27208 12.375 9 12.375C12.7279 12.375 15.75 11.3529 15.75 10.125"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function SigninWithPassword() {
  const [data, setData] = useState({
    db: process.env.NEXT_PUBLIC_ODOO_DEFAULT_DB || "",
    login: process.env.NEXT_PUBLIC_DEMO_USER_MAIL || "",
    password: process.env.NEXT_PUBLIC_DEMO_USER_PASS || "",
    remember: false,
  });

  const [error, setError] = useState<string>("");
  const [isPending, startTransition] = useTransition();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setData({
      ...data,
      [e.target.name]: e.target.value,
    });
    // Clear error when user starts typing
    if (error) {
      setError("");
    }
  };

  async function handleSubmit(formData: FormData) {
    setError("");
    
    startTransition(async () => {
      const result = await login(formData);
      
      if (!result.success) {
        setError(result.error || "Login failed. Please check your credentials.");
      }
      // On success, login() will redirect automatically to /
    });
  }

  return (
    <form action={handleSubmit}>
      {/* Database Field */}
      <InputGroup
        type="text"
        label="Database"
        className="mb-4 [&_input]:py-[15px]"
        placeholder="Enter database name"
        name="db"
        handleChange={handleChange}
        value={data.db}
        required
        icon={<DatabaseIcon className="size-5 text-dark-4 dark:text-dark-6" />}
      />

      {/* Email Field */}
      <InputGroup
        type="email"
        label="Email"
        className="mb-4 [&_input]:py-[15px]"
        placeholder="Enter your email"
        name="login"
        handleChange={handleChange}
        value={data.login}
        required
        icon={<EmailIcon />}
      />

      {/* Password Field */}
      <InputGroup
        type="password"
        label="Password"
        className="mb-5 [&_input]:py-[15px]"
        placeholder="Enter your password"
        name="password"
        handleChange={handleChange}
        value={data.password}
        required
        icon={<PasswordIcon />}
      />

      {/* Error Message */}
      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      )}

      <div className="mb-6 flex items-center justify-between gap-2 py-2 font-medium">
        <Checkbox
          label="Remember me"
          name="remember"
          withIcon="check"
          minimal
          radius="md"
          onChange={(e) =>
            setData({
              ...data,
              remember: e.target.checked,
            })
          }
        />

        <Link
          href="/auth/forgot-password"
          className="hover:text-primary dark:text-white dark:hover:text-primary"
        >
          Forgot Password?
        </Link>
      </div>

      <div className="mb-4.5">
        <button
          type="submit"
          disabled={isPending}
          className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-primary p-4 font-medium text-white transition hover:bg-opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isPending ? (
            <>
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-white border-t-transparent dark:border-primary dark:border-t-transparent" />
              Signing in...
            </>
          ) : (
            "Sign In"
          )}
        </button>
      </div>
    </form>
  );
}
