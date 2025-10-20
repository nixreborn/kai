import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <ThemeToggle />

      <div className="max-w-4xl mx-auto text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent">
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
          <div className="p-6 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-xl font-semibold mb-2 text-blue-600 dark:text-blue-400">
              AI-Driven Journaling
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Document your journey with intelligent prompts and insights
            </p>
          </div>

          <div className="p-6 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-xl font-semibold mb-2 text-cyan-600 dark:text-cyan-400">
              Proactive Support
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Receive personalized reminders and mental wellness guidance
            </p>
          </div>

          <div className="p-6 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-xl font-semibold mb-2 text-purple-600 dark:text-purple-400">
              Water Therapy
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Connect with calming aqua-themed mindfulness practices
            </p>
          </div>

          <div className="p-6 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-xl font-semibold mb-2 text-green-600 dark:text-green-400">
              Privacy First
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Your data is encrypted and secure. You&apos;re in control.
            </p>
          </div>
        </div>

        <div className="mt-12">
          <Link href="/chat">
            <button className="px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-lg font-semibold text-lg transition-all shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95">
              Start Your Journey
            </button>
          </Link>
        </div>

        <div className="mt-8 text-sm text-gray-500 dark:text-gray-400">
          <p>Phase 1: Core Infrastructure - In Development</p>
        </div>
      </div>
    </main>
  );
}
