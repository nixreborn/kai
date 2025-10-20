'use client';

import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/chat');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-aqua-600 dark:text-aqua-400" />
      </main>
    );
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 relative">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="max-w-4xl mx-auto text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-aqua-600 to-ocean-600 dark:from-aqua-400 dark:to-ocean-400 bg-clip-text text-transparent">
            Kai
          </h1>
          <p className="text-2xl text-gray-600 dark:text-gray-300">
            Your Mental Wellness Companion
          </p>
          <p className="text-lg text-gray-500 dark:text-gray-400 italic">
            &quot;Be the person you needed&quot;
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
          <div className="p-6 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:border-aqua-400 dark:hover:border-aqua-600 transition-colors">
            <h3 className="text-xl font-semibold mb-2 text-aqua-600 dark:text-aqua-400">
              AI-Driven Support
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Receive empathetic responses and personalized guidance
            </p>
          </div>

          <div className="p-6 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:border-ocean-400 dark:hover:border-ocean-600 transition-colors">
            <h3 className="text-xl font-semibold mb-2 text-ocean-600 dark:text-ocean-400">
              Proactive Check-ins
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Kai reaches out with thoughtful prompts and reminders
            </p>
          </div>

          <div className="p-6 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:border-calm-400 dark:hover:border-calm-600 transition-colors">
            <h3 className="text-xl font-semibold mb-2 text-calm-600 dark:text-calm-400">
              Calming Design
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Water-inspired theme promotes peace and relaxation
            </p>
          </div>

          <div className="p-6 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:border-green-400 dark:hover:border-green-600 transition-colors">
            <h3 className="text-xl font-semibold mb-2 text-green-600 dark:text-green-400">
              Privacy First
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Your conversations are private and encrypted
            </p>
          </div>
        </div>

        <div className="mt-12 flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/auth/register">
            <button className="px-8 py-4 bg-gradient-to-r from-aqua-600 to-ocean-600 hover:from-aqua-700 hover:to-ocean-700 text-white rounded-lg font-semibold text-lg transition-all shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95">
              Start Your Journey
            </button>
          </Link>
          <Link href="/auth/login">
            <button className="px-8 py-4 bg-white dark:bg-gray-800 border-2 border-aqua-600 dark:border-aqua-400 text-aqua-600 dark:text-aqua-400 hover:bg-aqua-50 dark:hover:bg-gray-700 rounded-lg font-semibold text-lg transition-all shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95">
              Sign In
            </button>
          </Link>
        </div>

        <div className="mt-8 text-sm text-gray-500 dark:text-gray-400">
          <p>In crisis? <a href="tel:988" className="text-aqua-600 dark:text-aqua-400 hover:underline font-medium">Call 988</a> for immediate support</p>
        </div>
      </div>
    </main>
  );
}
