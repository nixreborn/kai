/**
 * TypingIndicator component - Shows animated dots when Kai is thinking
 */

'use client';

export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-2 px-4 py-3 rounded-2xl bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/30 dark:to-ocean-950/30 border border-aqua-200 dark:border-aqua-800 max-w-[100px]" aria-label="Kai is typing">
      <div className="flex space-x-1">
        <span className="w-2 h-2 bg-aqua-500 dark:bg-aqua-400 rounded-full animate-wave" style={{ animationDelay: '0ms' }}></span>
        <span className="w-2 h-2 bg-ocean-500 dark:bg-ocean-400 rounded-full animate-wave" style={{ animationDelay: '150ms' }}></span>
        <span className="w-2 h-2 bg-calm-500 dark:bg-calm-400 rounded-full animate-wave" style={{ animationDelay: '300ms' }}></span>
      </div>
    </div>
  );
}
