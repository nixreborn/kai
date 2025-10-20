/**
 * Login page
 */

import { LoginForm } from '@/components/auth/LoginForm';
import { ThemeToggle } from '@/components/theme-toggle';
import Link from 'next/link';

export const metadata = {
  title: 'Sign in - Kai',
  description: 'Sign in to your Kai account',
};

export default function LoginPage() {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-aqua-500 via-ocean-600 to-calm-600 p-12 flex-col justify-between relative overflow-hidden">
        {/* Animated background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-64 h-64 bg-white rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
        </div>

        <div className="relative z-10">
          <Link href="/" className="inline-block">
            <h1 className="text-4xl font-bold text-white mb-2">Kai</h1>
          </Link>
          <p className="text-aqua-100 text-lg">Your mental wellness companion</p>
        </div>

        <div className="relative z-10 space-y-6">
          <div className="space-y-4">
            <h2 className="text-3xl font-semibold text-white">
              Welcome back to your journey
            </h2>
            <p className="text-aqua-100 text-lg leading-relaxed">
              Continue your path to better mental wellness. Kai is here to listen, support, and
              guide you.
            </p>
          </div>

          <div className="space-y-4 pt-6">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0 mt-1">
                <span className="text-white font-semibold">1</span>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Private & Secure</h3>
                <p className="text-aqua-100 text-sm">
                  Your conversations are encrypted and private
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0 mt-1">
                <span className="text-white font-semibold">2</span>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">AI-Powered Support</h3>
                <p className="text-aqua-100 text-sm">
                  Get personalized guidance and emotional support
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0 mt-1">
                <span className="text-white font-semibold">3</span>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">Available 24/7</h3>
                <p className="text-aqua-100 text-sm">
                  Support whenever you need it, day or night
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-aqua-100 text-sm">
            Be the person you needed.
          </p>
        </div>
      </div>

      {/* Right side - Login form */}
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
                Sign in to your account
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Continue your mental wellness journey
              </p>
            </div>

            <LoginForm />

            {/* Crisis support note */}
            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <p className="text-xs text-center text-gray-500 dark:text-gray-400">
                In crisis?{' '}
                <a
                  href="tel:988"
                  className="text-aqua-600 dark:text-aqua-400 hover:underline font-medium"
                >
                  Call 988
                </a>{' '}
                for immediate support
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
