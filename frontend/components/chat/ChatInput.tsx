/**
 * ChatInput component - Text input with auto-resize and keyboard shortcuts
 */

'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  isLoading = false,
  disabled = false,
  placeholder = 'Share your thoughts with Kai...',
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [message]);

  // Focus on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleSend = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !isLoading && !disabled) {
      onSend(trimmedMessage);
      setMessage('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative flex items-end gap-2 p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          rows={1}
          className="w-full px-4 py-3 pr-12 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-aqua-500 dark:focus:ring-aqua-400 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ minHeight: '48px', maxHeight: '200px' }}
          aria-label="Message input"
        />

        {/* Character count (optional) */}
        {message.length > 0 && (
          <div className="absolute bottom-2 right-2 text-xs text-gray-400 dark:text-gray-500">
            {message.length}
          </div>
        )}
      </div>

      <button
        onClick={handleSend}
        disabled={!message.trim() || isLoading || disabled}
        className="flex-shrink-0 p-3 rounded-full bg-gradient-to-br from-aqua-500 to-ocean-500 hover:from-aqua-600 hover:to-ocean-600 text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-aqua-500 dark:focus:ring-aqua-400 focus:ring-offset-2 shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95"
        aria-label="Send message"
        title="Send message (Enter)"
      >
        {isLoading ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          <Send className="w-5 h-5" />
        )}
      </button>

      {/* Keyboard shortcut hint */}
      <div className="absolute -top-8 right-4 text-xs text-gray-500 dark:text-gray-400">
        <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-700">
          Enter
        </kbd>
        {' '}to send • {' '}
        <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-700">
          Shift + Enter
        </kbd>
        {' '}for new line
      </div>
    </div>
  );
}
