/**
 * ChatContainer component - Scrollable message list with auto-scroll
 */

'use client';

import { useEffect, useRef } from 'react';
import { Message } from '@/lib/types/chat';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';
import { Waves } from 'lucide-react';

interface ChatContainerProps {
  messages: Message[];
  isLoading?: boolean;
}

export function ChatContainer({ messages, isLoading = false }: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const prevMessageCountRef = useRef(messages.length);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > prevMessageCountRef.current || isLoading) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
    prevMessageCountRef.current = messages.length;
  }, [messages.length, isLoading]);

  // Empty state
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-aqua-500 to-ocean-500 flex items-center justify-center mb-4 shadow-lg animate-pulse-slow">
          <Waves className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
          Welcome to Kai
        </h2>
        <p className="text-gray-600 dark:text-gray-400 max-w-md mb-6">
          Your mental wellness companion is here to listen and support you. Share your thoughts, feelings, or simply say hello.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
          <SuggestionCard
            emoji="💭"
            text="How are you feeling today?"
          />
          <SuggestionCard
            emoji="📝"
            text="I want to journal about my day"
          />
          <SuggestionCard
            emoji="🌊"
            text="I need some calming exercises"
          />
          <SuggestionCard
            emoji="💡"
            text="Help me understand my emotions"
          />
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto scroll-smooth px-4 py-6"
      role="log"
      aria-live="polite"
      aria-label="Chat messages"
    >
      <div className="max-w-4xl mx-auto space-y-6">
        {messages.map((message) => (
          <div key={message.id} className="group">
            <ChatMessage message={message} />
          </div>
        ))}

        {isLoading && (
          <div className="flex">
            <TypingIndicator />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

interface SuggestionCardProps {
  emoji: string;
  text: string;
}

function SuggestionCard({ emoji, text }: SuggestionCardProps) {
  return (
    <div className="p-4 rounded-xl bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/20 dark:to-ocean-950/20 border border-aqua-200 dark:border-aqua-800 hover:border-aqua-400 dark:hover:border-aqua-600 transition-all cursor-pointer hover:shadow-md group">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{emoji}</span>
        <p className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-aqua-700 dark:group-hover:text-aqua-300 transition-colors">
          {text}
        </p>
      </div>
    </div>
  );
}
