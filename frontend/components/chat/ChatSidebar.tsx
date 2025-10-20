/**
 * ChatSidebar component - Conversation history and session management
 */

'use client';

import { ConversationSession } from '@/lib/types/chat';
import { format, isToday, isYesterday, isThisWeek } from 'date-fns';
import {
  MessageSquare,
  Plus,
  Trash2,
  Download,
  Settings,
  Moon,
  Sun,
  Menu,
  X,
} from 'lucide-react';
import { useState } from 'react';
import { useTheme } from 'next-themes';

interface ChatSidebarProps {
  sessions: ConversationSession[];
  currentSession: ConversationSession | null;
  onSessionSelect: (sessionId: string) => void;
  onNewSession: () => void;
  onDeleteSession: (sessionId: string) => void;
  onExportConversation?: () => void;
  onClearConversation?: () => void;
  userTraits?: Array<{ trait: string; value: string | number }>;
}

export function ChatSidebar({
  sessions,
  currentSession,
  onSessionSelect,
  onNewSession,
  onDeleteSession,
  onExportConversation,
  userTraits,
}: ChatSidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { theme, setTheme } = useTheme();

  const groupedSessions = groupSessionsByDate(sessions);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden p-2 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700"
        aria-label="Toggle sidebar"
      >
        {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-40 w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold bg-gradient-to-r from-aqua-600 to-ocean-600 dark:from-aqua-400 dark:to-ocean-400 bg-clip-text text-transparent">
              Kai
            </h2>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-5 h-5 text-yellow-500" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>
          </div>

          <button
            onClick={() => {
              onNewSession();
              setIsOpen(false);
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-aqua-500 to-ocean-500 hover:from-aqua-600 hover:to-ocean-600 text-white font-medium transition-all shadow-md hover:shadow-lg"
          >
            <Plus className="w-5 h-5" />
            New Conversation
          </button>
        </div>

        {/* User traits */}
        {userTraits && userTraits.length > 0 && (
          <div className="p-4 border-b border-gray-200 dark:border-gray-800">
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
              Your Profile
            </h3>
            <div className="space-y-1">
              {userTraits.slice(0, 3).map((trait, idx) => (
                <div key={idx} className="text-xs text-gray-600 dark:text-gray-300">
                  <span className="font-medium text-aqua-600 dark:text-aqua-400">{trait.trait}:</span>{' '}
                  {trait.value}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Conversation history */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">
            Conversations
          </h3>

          {sessions.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
              No conversations yet. Start a new one!
            </p>
          ) : (
            <div className="space-y-4">
              {Object.entries(groupedSessions).map(([group, groupSessions]) => (
                <div key={group}>
                  <h4 className="text-xs font-medium text-gray-400 dark:text-gray-500 mb-2">
                    {group}
                  </h4>
                  <div className="space-y-1">
                    {groupSessions.map((session) => (
                      <SessionItem
                        key={session.id}
                        session={session}
                        isActive={currentSession?.id === session.id}
                        onSelect={() => {
                          onSessionSelect(session.id);
                          setIsOpen(false);
                        }}
                        onDelete={() => onDeleteSession(session.id)}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-800 space-y-2">
          {onExportConversation && (
            <button
              onClick={onExportConversation}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              Export Conversation
            </button>
          )}
          <button
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </aside>
    </>
  );
}

interface SessionItemProps {
  session: ConversationSession;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

function SessionItem({ session, isActive, onSelect, onDelete }: SessionItemProps) {
  const [showDelete, setShowDelete] = useState(false);

  const previewText = session.messages[0]?.content.slice(0, 50) || 'New conversation';
  const messageCount = session.messages.length;

  return (
    <div
      className={`group relative p-3 rounded-lg cursor-pointer transition-all ${
        isActive
          ? 'bg-gradient-to-r from-aqua-50 to-ocean-50 dark:from-aqua-950/30 dark:to-ocean-950/30 border border-aqua-200 dark:border-aqua-800'
          : 'hover:bg-gray-50 dark:hover:bg-gray-800'
      }`}
      onClick={onSelect}
      onMouseEnter={() => setShowDelete(true)}
      onMouseLeave={() => setShowDelete(false)}
    >
      <div className="flex items-start gap-2">
        <MessageSquare className={`w-4 h-4 mt-1 flex-shrink-0 ${
          isActive ? 'text-aqua-600 dark:text-aqua-400' : 'text-gray-400'
        }`} />
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-800 dark:text-gray-200 truncate">
            {previewText}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {format(session.updated_at, 'MMM d, h:mm a')}
            </span>
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {messageCount} {messageCount === 1 ? 'message' : 'messages'}
            </span>
          </div>
        </div>

        {showDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="flex-shrink-0 p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition-colors"
            aria-label="Delete conversation"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}

function groupSessionsByDate(sessions: ConversationSession[]): Record<string, ConversationSession[]> {
  const groups: Record<string, ConversationSession[]> = {
    Today: [],
    Yesterday: [],
    'This Week': [],
    Earlier: [],
  };

  sessions
    .sort((a, b) => b.updated_at.getTime() - a.updated_at.getTime())
    .forEach((session) => {
      if (isToday(session.updated_at)) {
        groups.Today.push(session);
      } else if (isYesterday(session.updated_at)) {
        groups.Yesterday.push(session);
      } else if (isThisWeek(session.updated_at)) {
        groups['This Week'].push(session);
      } else {
        groups.Earlier.push(session);
      }
    });

  // Remove empty groups
  return Object.fromEntries(
    Object.entries(groups).filter(([, sessions]) => sessions.length > 0)
  );
}
