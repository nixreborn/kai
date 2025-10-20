/**
 * ChatMessage component - Displays individual chat messages with markdown support
 */

'use client';

import { Message } from '@/lib/types/chat';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import { User, Sparkles, Copy, CheckCheck, AlertTriangle } from 'lucide-react';
import { useState } from 'react';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const hasSafetyWarning = message.metadata?.safety_warning;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`flex gap-3 animate-slide-up ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
      role="article"
      aria-label={`${isUser ? 'Your' : 'Kai\'s'} message`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser
          ? 'bg-gradient-to-br from-blue-500 to-purple-500'
          : 'bg-gradient-to-br from-aqua-500 to-ocean-500'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Sparkles className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Message content */}
      <div className={`flex-1 max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Safety warning banner */}
        {hasSafetyWarning && (
          <div className="mb-2 px-3 py-2 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
            <p className="text-xs text-amber-700 dark:text-amber-300">
              This message may contain sensitive content. If you&apos;re in crisis, please contact a professional.
            </p>
          </div>
        )}

        {/* Message bubble */}
        <div
          className={`px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-gradient-to-br from-blue-600 to-cyan-600 text-white'
              : 'bg-gradient-to-br from-aqua-50 to-ocean-50 dark:from-aqua-950/30 dark:to-ocean-950/30 border border-aqua-200 dark:border-aqua-800'
          }`}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed prose-p:my-2 prose-headings:mb-2 prose-headings:mt-4 first:prose-headings:mt-0">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="text-sm text-gray-800 dark:text-gray-200">{children}</p>,
                  strong: ({ children }) => <strong className="font-semibold text-aqua-700 dark:text-aqua-300">{children}</strong>,
                  em: ({ children }) => <em className="italic text-gray-700 dark:text-gray-300">{children}</em>,
                  a: ({ href, children }) => (
                    <a href={href} className="text-ocean-600 dark:text-ocean-400 hover:underline" target="_blank" rel="noopener noreferrer">
                      {children}
                    </a>
                  ),
                  ul: ({ children }) => <ul className="list-disc list-inside my-2 space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside my-2 space-y-1">{children}</ol>,
                  li: ({ children }) => <li className="text-sm text-gray-800 dark:text-gray-200 ml-2">{children}</li>,
                  code: ({ children }) => (
                    <code className="px-1.5 py-0.5 rounded bg-aqua-100 dark:bg-aqua-900/30 text-aqua-800 dark:text-aqua-200 text-xs font-mono">
                      {children}
                    </code>
                  ),
                  pre: ({ children }) => (
                    <pre className="p-3 rounded-lg bg-gray-100 dark:bg-gray-800 overflow-x-auto my-2">
                      {children}
                    </pre>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Message footer */}
        <div className={`flex items-center gap-2 mt-1 px-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {format(message.timestamp, 'h:mm a')}
          </span>

          {!isUser && message.metadata?.agent_role && (
            <span className="text-xs text-aqua-600 dark:text-aqua-400 font-medium">
              {message.metadata.agent_role}
            </span>
          )}

          {!isUser && message.metadata?.confidence && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {Math.round(message.metadata.confidence * 100)}%
            </span>
          )}

          {/* Copy button */}
          <button
            onClick={handleCopy}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
            aria-label="Copy message"
            title="Copy message"
          >
            {copied ? (
              <CheckCheck className="w-3 h-3 text-green-600 dark:text-green-400" />
            ) : (
              <Copy className="w-3 h-3 text-gray-500 dark:text-gray-400" />
            )}
          </button>
        </div>

        {/* Wellness insights */}
        {message.metadata?.wellness_insights && message.metadata.wellness_insights.length > 0 && (
          <div className="mt-3 p-3 rounded-lg bg-calm-50 dark:bg-calm-950/20 border border-calm-200 dark:border-calm-800">
            <h4 className="text-xs font-semibold text-calm-700 dark:text-calm-300 mb-2">Wellness Insights</h4>
            <ul className="space-y-1">
              {message.metadata.wellness_insights.map((insight, idx) => (
                <li key={idx} className="text-xs text-gray-700 dark:text-gray-300">
                  <span className="font-medium text-calm-600 dark:text-calm-400">{insight.category}:</span> {insight.insight}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
