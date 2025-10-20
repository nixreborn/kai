/**
 * Password reset form component
 * Note: This is a placeholder UI. Backend password reset functionality would need to be implemented.
 */

'use client';

import { useState } from 'react';
import { isValidEmail } from '@/lib/api/auth';
import { Loader2, Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import Link from 'next/link';

export function PasswordResetForm() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email) {
      setError('Email is required');
      return;
    }

    if (!isValidEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setIsLoading(true);

    try {
      // TODO: Implement password reset API call
      // await resetPassword(email);

      // Simulate API call for now
      await new Promise(resolve => setTimeout(resolve, 1500));

      setEmailSent(true);
    } catch (err) {
      setError('Failed to send reset email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (emailSent) {
    return (
      <div className="text-center space-y-6">
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Check your email
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            We've sent password reset instructions to
          </p>
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{email}</p>
        </div>

        <div className="p-4 rounded-lg bg-aqua-50 dark:bg-aqua-900/20 border border-aqua-200 dark:border-aqua-800">
          <p className="text-sm text-aqua-800 dark:text-aqua-300">
            Didn't receive the email? Check your spam folder or try again in a few minutes.
          </p>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => {
              setEmailSent(false);
              setEmail('');
            }}
            className="w-full px-6 py-3 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            Try different email
          </button>

          <Link
            href="/auth/login"
            className="block w-full px-6 py-3 rounded-lg bg-aqua-600 hover:bg-aqua-700 dark:bg-aqua-700 dark:hover:bg-aqua-600 text-white font-medium text-center transition-colors"
          >
            Back to sign in
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          Reset your password
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Enter your email address and we'll send you instructions to reset your password.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Email address
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setError('');
            }}
            className={`w-full px-4 py-3 rounded-lg border ${
              error
                ? 'border-red-300 dark:border-red-700 focus:ring-red-500 focus:border-red-500'
                : 'border-gray-300 dark:border-gray-600 focus:ring-aqua-500 focus:border-aqua-500'
            } bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 transition-colors`}
            placeholder="you@example.com"
            disabled={isLoading}
          />
          {error && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>}
        </div>

        <div className="space-y-3">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-aqua-600 hover:bg-aqua-700 dark:bg-aqua-700 dark:hover:bg-aqua-600 text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-aqua-500 focus:ring-offset-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Mail className="w-5 h-5" />
                Send reset instructions
              </>
            )}
          </button>

          <Link
            href="/auth/login"
            className="flex items-center justify-center gap-2 w-full px-6 py-3 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to sign in
          </Link>
        </div>
      </form>

      <div className="p-4 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
        <p className="text-xs text-amber-800 dark:text-amber-300">
          Note: Password reset functionality is not yet fully implemented on the backend. This is a
          UI placeholder.
        </p>
      </div>
    </div>
  );
}
