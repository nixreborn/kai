/**
 * Registration page
 */

import { RegisterForm } from '@/components/auth/RegisterForm';
import { ThemeToggle } from '@/components/theme-toggle';
import Link from 'next/link';

export const metadata = {
  title: 'Create account - Kai',
  description: 'Create your Kai account',
};

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-calm-500 via-aqua-600 to-ocean-600 p-12 flex-col justify-between relative overflow-hidden">
        {/* Animated background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-64 h-64 bg-white rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
        </div>

        <div className="relative z-10">
          <Link href="/" className="inline-block">
            <h1 className="text-4xl font-bold text-white mb-2">Kai</h1>
          </Link>
          <p className="text-calm-100 text-lg">Your mental wellness companion</p>
        </div>

        <div className="relative z-10 space-y-6">
          <div className="space-y-4">
            <h2 className="text-3xl font-semibold text-white">
              Start your wellness journey today
            </h2>
            <p className="text-calm-100 text-lg leading-relaxed">
              Join thousands of people improving their mental health with Kai's AI-powered support
              and guidance.
            </p>
          </div>

          <div className="space-y-4 pt-6">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0 mt-1">
                <svg
                  className="w-4 h-4 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Free to start</h3>
                <p className="text-calm-100 text-sm">
                  Create your account and begin your journey at no cost
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0 mt-1">
                <svg
                  className="w-4 h-4 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Personalized experience</h3>
                <p className="text-calm-100 text-sm">
                  Kai learns your preferences and adapts to your needs
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0 mt-1">
                <svg
                  className="w-4 h-4 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Your data is safe</h3>
                <p className="text-calm-100 text-sm">
                  End-to-end encryption and privacy-first design
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="relative z-10">
          <blockquote className="border-l-4 border-white/30 pl-4">
            <p className="text-white italic text-sm mb-2">
              "Kai has helped me understand my emotions better and develop healthier coping
              strategies."
            </p>
            <footer className="text-calm-100 text-xs">- Sarah, Kai user</footer>
          </blockquote>
        </div>
      </div>

      {/* Right side - Register form */}
      <div className="flex-1 flex flex-col">
        <div className="flex justify-end p-6">
          <ThemeToggle />
        </div>

        <div className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-md space-y-8">
            {/* Mobile branding */}
            <div className="lg:hidden text-center">
              <Link href="/">
                <h1 className="text-3xl font-bold text-aqua-600 dark:text-aqua-400 mb-2">Kai</h1>
              </Link>
              <p className="text-gray-600 dark:text-gray-400">Your mental wellness companion</p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                Create your account
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Begin your journey to better mental wellness
              </p>
            </div>

            <RegisterForm />

            {/* Terms and privacy */}
            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <p className="text-xs text-center text-gray-500 dark:text-gray-400">
                By creating an account, you agree to our{' '}
                <a
                  href="/terms"
                  className="text-aqua-600 dark:text-aqua-400 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Terms of Service
                </a>{' '}
                and{' '}
                <a
                  href="/privacy"
                  className="text-aqua-600 dark:text-aqua-400 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Privacy Policy
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
