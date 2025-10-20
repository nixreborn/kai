/**
 * Custom hook for chat functionality
 */

'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { Message, ConversationSession, WellnessInsight, UserTrait } from '@/lib/types/chat';
import { sendMessage, clearSession as apiClearSession } from '@/lib/api/chat';

const STORAGE_KEY = 'kai-chat-sessions';
const CURRENT_SESSION_KEY = 'kai-current-session';

interface UseChatOptions {
  userId: string;
  sessionId?: string;
  autoSave?: boolean;
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendChatMessage: (content: string) => Promise<void>;
  clearConversation: () => Promise<void>;
  retryLastMessage: () => Promise<void>;
  sessions: ConversationSession[];
  currentSession: ConversationSession | null;
  loadSession: (sessionId: string) => void;
  createNewSession: () => void;
  deleteSession: (sessionId: string) => void;
}

export function useChat({ userId, sessionId, autoSave = true }: UseChatOptions): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>(sessionId || '');
  const abortControllerRef = useRef<AbortController | null>(null);
  const lastUserMessageRef = useRef<string>('');

  // Load sessions from localStorage
  useEffect(() => {
    if (typeof window === 'undefined') return;

    let sessionsWithDates: ConversationSession[] = [];
    const storedSessions = localStorage.getItem(STORAGE_KEY);
    if (storedSessions) {
      const parsed = JSON.parse(storedSessions);
      // Convert date strings back to Date objects
      sessionsWithDates = parsed.map((session: ConversationSession) => ({
        ...session,
        created_at: new Date(session.created_at),
        updated_at: new Date(session.updated_at),
        messages: session.messages.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })),
      }));
      setSessions(sessionsWithDates);
    }

    // Load or create current session
    const storedCurrentSessionId = localStorage.getItem(CURRENT_SESSION_KEY);
    if (storedCurrentSessionId && !sessionId) {
      setCurrentSessionId(storedCurrentSessionId);
      const session = sessionsWithDates.find((s: ConversationSession) => s.id === storedCurrentSessionId);
      if (session) {
        setMessages(session.messages);
      }
    } else if (!currentSessionId) {
      // Create new session
      const newSessionId = `session-${Date.now()}`;
      setCurrentSessionId(newSessionId);
      localStorage.setItem(CURRENT_SESSION_KEY, newSessionId);
    }
  }, [sessionId, currentSessionId]);

  // Save sessions to localStorage
  useEffect(() => {
    if (!autoSave || typeof window === 'undefined') return;

    const currentSession = sessions.find(s => s.id === currentSessionId);
    const now = new Date();

    if (currentSession) {
      // Update existing session
      const updatedSessions = sessions.map(s =>
        s.id === currentSessionId
          ? { ...s, messages, updated_at: now }
          : s
      );
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSessions));
      setSessions(updatedSessions);
    } else if (messages.length > 0) {
      // Create new session
      const newSession: ConversationSession = {
        id: currentSessionId || `session-${Date.now()}`,
        user_id: userId,
        messages,
        created_at: now,
        updated_at: now,
      };
      const updatedSessions = [...sessions, newSession];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSessions));
      setSessions(updatedSessions);
    }
  }, [messages, currentSessionId, userId, autoSave, sessions]);

  const sendChatMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setError(null);
    setIsLoading(true);
    lastUserMessageRef.current = content;

    // Add user message
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    // Cancel any pending requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    try {
      // Prepare conversation history for API
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await sendMessage(
        {
          user_id: userId,
          message: content.trim(),
          conversation_history: conversationHistory,
        },
        {
          signal: abortControllerRef.current.signal,
        }
      );

      // Add assistant message
      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        metadata: {
          agent_role: response.metadata.agent_role as 'kai' | 'guardrail' | 'genetic' | 'wellness',
          confidence: response.metadata.confidence,
          safety_warning: response.metadata.safety_warning as boolean | undefined,
          wellness_insights: response.metadata.wellness_insights as WellnessInsight[] | undefined,
          user_traits: response.metadata.user_traits as UserTrait[] | undefined,
        },
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        return; // Request was cancelled, ignore
      }

      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      // Add error message to chat
      const errorMsg: Message = {
        id: `msg-${Date.now()}-error`,
        role: 'assistant',
        content: `I'm having trouble connecting right now. ${errorMessage}. Please try again.`,
        timestamp: new Date(),
        metadata: { agent_role: 'kai' },
      };

      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [userId, messages]);

  const retryLastMessage = useCallback(async () => {
    if (lastUserMessageRef.current) {
      // Remove the last two messages (user message and error response)
      setMessages(prev => prev.slice(0, -2));
      await sendChatMessage(lastUserMessageRef.current);
    }
  }, [sendChatMessage]);

  const clearConversation = useCallback(async () => {
    try {
      await apiClearSession(userId);
      setMessages([]);
      setError(null);
      lastUserMessageRef.current = '';
    } catch (err) {
      console.error('Error clearing session:', err);
      setError('Failed to clear conversation');
    }
  }, [userId]);

  const loadSession = useCallback((sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
      setMessages(session.messages);
      setCurrentSessionId(sessionId);
      localStorage.setItem(CURRENT_SESSION_KEY, sessionId);
    }
  }, [sessions]);

  const createNewSession = useCallback(() => {
    const newSessionId = `session-${Date.now()}`;
    setCurrentSessionId(newSessionId);
    setMessages([]);
    localStorage.setItem(CURRENT_SESSION_KEY, newSessionId);
  }, []);

  const deleteSession = useCallback((sessionId: string) => {
    const updatedSessions = sessions.filter(s => s.id !== sessionId);
    setSessions(updatedSessions);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSessions));

    if (sessionId === currentSessionId) {
      createNewSession();
    }
  }, [sessions, currentSessionId, createNewSession]);

  const currentSession = sessions.find(s => s.id === currentSessionId) || null;

  return {
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
  };
}
