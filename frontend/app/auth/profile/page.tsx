/**
 * User profile page
 */

'use client';

import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { format } from 'date-fns';
import { User, Mail, Calendar, Shield, LogOut, ArrowLeft, Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function ProfilePage() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
      setIsLoggingOut(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin text-aqua-600 dark:text-aqua-400 mx-auto" />
          <p className="text-gray-600 dark:text-gray-400">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/chat"
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  Your Profile
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Manage your account settings
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Profile card */}
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 overflow-hidden">
            {/* Cover with gradient */}
            <div className="h-32 bg-gradient-to-r from-aqua-500 via-ocean-600 to-calm-600" />

            {/* Profile info */}
            <div className="px-6 pb-6">
              <div className="flex items-start gap-6 -mt-16">
                {/* Avatar */}
                <div className="w-32 h-32 rounded-full bg-white dark:bg-gray-900 p-2 shadow-lg">
                  <div className="w-full h-full rounded-full bg-gradient-to-br from-aqua-400 to-calm-500 flex items-center justify-center">
                    <User className="w-16 h-16 text-white" />
                  </div>
                </div>

                {/* User details */}
                <div className="flex-1 pt-20">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {user.email.split('@')[0]}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">Kai user</p>
                </div>
              </div>

              {/* Account details */}
              <div className="mt-8 space-y-4">
                <div className="flex items-start gap-3 p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <Mail className="w-5 h-5 text-gray-600 dark:text-gray-400 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      Email address
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{user.email}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <Calendar className="w-5 h-5 text-gray-600 dark:text-gray-400 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      Member since
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {format(new Date(user.created_at), 'MMMM d, yyyy')}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <Shield className="w-5 h-5 text-gray-600 dark:text-gray-400 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      Account status
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          user.is_active ? 'bg-green-500' : 'bg-red-500'
                        }`}
                      />
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {user.is_active ? 'Active' : 'Inactive'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Privacy & Security section */}
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Privacy & Security
            </h3>
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-aqua-50 dark:bg-aqua-900/20 border border-aqua-200 dark:border-aqua-800">
                <p className="text-sm text-aqua-800 dark:text-aqua-300">
                  Your conversations with Kai are private and encrypted. We take your privacy
                  seriously and never share your personal information.
                </p>
              </div>

              <div className="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    Two-factor authentication
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    Coming soon
                  </p>
                </div>
                <div className="px-3 py-1 rounded-full bg-gray-200 dark:bg-gray-700 text-xs font-medium text-gray-700 dark:text-gray-300">
                  Not available
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Account Actions
            </h3>
            <div className="space-y-3">
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 font-medium hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoggingOut ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Logging out...
                  </>
                ) : (
                  <>
                    <LogOut className="w-5 h-5" />
                    Sign out
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Support info */}
          <div className="p-6 rounded-xl bg-gradient-to-br from-aqua-50 to-calm-50 dark:from-aqua-900/20 dark:to-calm-900/20 border border-aqua-200 dark:border-aqua-800">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Need help?
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              If you're in crisis or need immediate support, please reach out to a professional.
            </p>
            <a
              href="tel:988"
              className="inline-flex items-center gap-2 text-sm font-medium text-aqua-600 dark:text-aqua-400 hover:underline"
            >
              Call 988 for crisis support
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}
