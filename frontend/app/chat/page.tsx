/**
 * Chat page - Main chat interface for Kai
 */

'use client';

import { useChat } from '@/hooks/useChat';
import { ChatSidebar } from '@/components/chat/ChatSidebar';
import { ChatContainer } from '@/components/chat/ChatContainer';
import { ChatInput } from '@/components/chat/ChatInput';
import { useState, useEffect } from 'react';
import { AlertCircle, RefreshCw, Download } from 'lucide-react';
import { checkHealth } from '@/lib/api/chat';

// Generate a simple user ID (in production, this would come from auth)
const getUserId = () => {
  if (typeof window === 'undefined') return 'demo-user';

  let userId = localStorage.getItem('kai-user-id');
  if (!userId) {
    userId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('kai-user-id', userId);
  }
  return userId;
};

export default function ChatPage() {
  const [userId] = useState(getUserId);
  const [apiHealth, setApiHealth] = useState<boolean | null>(null);
  const [showHealthWarning, setShowHealthWarning] = useState(false);

  const {
    messages,
    isLoading,
    error,
    sendChatMessage,
    clearConversation,
    retryLastMessage,
    sessions,
    currentSession,
    loadSession,
    createNewSession,
    deleteSession,
  } = useChat({ userId, autoSave: true });

  // Check API health on mount
  useEffect(() => {
    checkHealth().then((healthy) => {
      setApiHealth(healthy);
      if (!healthy) {
        setShowHealthWarning(true);
      }
    });

    // Periodic health check every 30 seconds
    const interval = setInterval(() => {
      checkHealth().then((healthy) => {
        setApiHealth(healthy);
        if (!healthy && !showHealthWarning) {
          setShowHealthWarning(true);
        } else if (healthy && showHealthWarning) {
          setShowHealthWarning(false);
        }
      });
    }, 30000);

    return () => clearInterval(interval);
  }, [showHealthWarning]);

  const handleExportConversation = () => {
    if (!currentSession) return;

    const conversationText = currentSession.messages
      .map((msg) => `${msg.role === 'user' ? 'You' : 'Kai'}: ${msg.content}`)
      .join('\n\n');

    const blob = new Blob([conversationText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `kai-conversation-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">
      {/* Sidebar */}
      <ChatSidebar
        sessions={sessions}
        currentSession={currentSession}
        onSessionSelect={loadSession}
        onNewSession={createNewSession}
        onDeleteSession={deleteSession}
        onExportConversation={handleExportConversation}
        onClearConversation={clearConversation}
      />

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
          <div>
            <h1 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
              Chat with Kai
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Your mental wellness companion
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* API Health indicator */}
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  apiHealth === null
                    ? 'bg-gray-400'
                    : apiHealth
                    ? 'bg-green-500 animate-pulse'
                    : 'bg-red-500 animate-pulse'
                }`}
              />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                {apiHealth === null ? 'Checking...' : apiHealth ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Export button */}
            {messages.length > 0 && (
              <button
                onClick={handleExportConversation}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Export conversation"
                title="Export conversation"
              >
                <Download className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
            )}
          </div>
        </header>

        {/* API Health warning */}
        {showHealthWarning && !apiHealth && (
          <div className="mx-6 mt-4 p-4 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-amber-800 dark:text-amber-300 mb-1">
                Cannot connect to Kai backend
              </h3>
              <p className="text-xs text-amber-700 dark:text-amber-400 mb-2">
                Make sure the backend server is running at http://localhost:8000
              </p>
              <button
                onClick={() => checkHealth().then(setApiHealth)}
                className="text-xs text-amber-600 dark:text-amber-400 font-medium hover:underline flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" />
                Retry connection
              </button>
            </div>
            <button
              onClick={() => setShowHealthWarning(false)}
              className="text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300"
              aria-label="Dismiss"
            >
              ×
            </button>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="mx-6 mt-4 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-red-800 dark:text-red-300 mb-1">
                Error
              </h3>
              <p className="text-xs text-red-700 dark:text-red-400">{error}</p>
            </div>
            <button
              onClick={retryLastMessage}
              className="text-xs text-red-600 dark:text-red-400 font-medium hover:underline flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" />
              Retry
            </button>
          </div>
        )}

        {/* Messages */}
        <ChatContainer messages={messages} isLoading={isLoading} />

        {/* Input */}
        <ChatInput
          onSend={sendChatMessage}
          isLoading={isLoading}
          disabled={!apiHealth}
        />

        {/* Footer */}
        <div className="px-6 py-3 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
          <p className="text-xs text-center text-gray-500 dark:text-gray-400">
            Kai is an AI companion. For emergencies, please contact professional help.{' '}
            <a
              href="tel:988"
              className="text-aqua-600 dark:text-aqua-400 hover:underline font-medium"
            >
              Crisis: 988
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
