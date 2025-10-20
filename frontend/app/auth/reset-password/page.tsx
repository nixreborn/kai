/**
 * Password reset page
 */

import { PasswordResetForm } from '@/components/auth/PasswordResetForm';
import { ThemeToggle } from '@/components/theme-toggle';
import Link from 'next/link';

export const metadata = {
  title: 'Reset password - Kai',
  description: 'Reset your Kai account password',
};

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-ocean-500 via-aqua-600 to-calm-600 p-12 flex-col justify-between relative overflow-hidden">
        {/* Animated background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-64 h-64 bg-white rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
        </div>

        <div className="relative z-10">
          <Link href="/" className="inline-block">
            <h1 className="text-4xl font-bold text-white mb-2">Kai</h1>
          </Link>
          <p className="text-ocean-100 text-lg">Your mental wellness companion</p>
        </div>

        <div className="relative z-10 space-y-6">
          <div className="space-y-4">
            <h2 className="text-3xl font-semibold text-white">
              We're here to help
            </h2>
            <p className="text-ocean-100 text-lg leading-relaxed">
              Forgot your password? No worries. We'll help you get back to your wellness journey
              in just a few steps.
            </p>
          </div>

          <div className="space-y-4 pt-6">
            <div className="p-6 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20">
              <h3 className="text-white font-semibold mb-3">Need help?</h3>
              <p className="text-ocean-100 text-sm mb-4">
                If you're having trouble resetting your password or accessing your account, we're
                here to support you.
              </p>
              <a
                href="mailto:support@kai.example.com"
                className="text-white text-sm font-medium hover:underline"
              >
                Contact support
              </a>
            </div>
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-ocean-100 text-sm">
            Your privacy and security are our top priorities.
          </p>
        </div>
      </div>

      {/* Right side - Reset form */}
      <div className="flex-1 flex flex-col">
        <div className="flex justify-end p-6">
          <ThemeToggle />
        </div>

        <div className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-md space-y-8">
            {/* Mobile branding */}
            <div className="lg:hidden text-center mb-8">
              <Link href="/">
                <h1 className="text-3xl font-bold text-aqua-600 dark:text-aqua-400 mb-2">Kai</h1>
              </Link>
              <p className="text-gray-600 dark:text-gray-400">Your mental wellness companion</p>
            </div>

            <PasswordResetForm />
          </div>
        </div>
      </div>
    </div>
  );
}
