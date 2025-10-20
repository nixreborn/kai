import { renderHook, act, waitFor } from '@testing-library/react'
import { useChat } from '@/hooks/useChat'
import * as chatApi from '@/lib/api/chat'
import { server } from '@/__tests__/mocks/server'
import { http, HttpResponse } from 'msw'

// Mock the chat API
jest.mock('@/lib/api/chat')

const mockSendMessage = chatApi.sendMessage as jest.MockedFunction<typeof chatApi.sendMessage>
const mockClearSession = chatApi.clearSession as jest.MockedFunction<typeof chatApi.clearSession>

describe('useChat', () => {
  const userId = 'test-user-123'

  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  describe('Initialization', () => {
    it('initializes with empty messages', () => {
      const { result } = renderHook(() => useChat({ userId }))

      expect(result.current.messages).toEqual([])
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('creates a new session on initialization', () => {
      const { result } = renderHook(() => useChat({ userId }))

      expect(result.current.currentSession).toBeDefined()
    })

    it('loads existing session from localStorage', () => {
      const existingSession = {
        id: 'session-123',
        user_id: userId,
        messages: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'Hello',
            timestamp: new Date().toISOString(),
          },
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      localStorage.setItem('kai-chat-sessions', JSON.stringify([existingSession]))
      localStorage.setItem('kai-current-session', 'session-123')

      const { result } = renderHook(() => useChat({ userId }))

      expect(result.current.messages).toHaveLength(1)
      expect(result.current.messages[0].content).toBe('Hello')
    })
  })

  describe('sendChatMessage', () => {
    it('adds user message immediately', async () => {
      mockSendMessage.mockResolvedValue({
        response: 'Test response',
        metadata: {
          agent_role: 'kai',
          confidence: 0.95,
        },
      })

      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('Hello Kai')
      })

      expect(result.current.messages[0].content).toBe('Hello Kai')
      expect(result.current.messages[0].role).toBe('user')
    })

    it('adds assistant response after API call', async () => {
      mockSendMessage.mockResolvedValue({
        response: 'Test response from Kai',
        metadata: {
          agent_role: 'kai',
          confidence: 0.95,
        },
      })

      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('Hello Kai')
      })

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(2)
      })

      expect(result.current.messages[1].content).toBe('Test response from Kai')
      expect(result.current.messages[1].role).toBe('assistant')
      expect(result.current.messages[1].metadata?.agent_role).toBe('kai')
    })

    it('sets loading state during API call', async () => {
      mockSendMessage.mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      )

      const { result } = renderHook(() => useChat({ userId }))

      act(() => {
        result.current.sendChatMessage('Test')
      })

      expect(result.current.isLoading).toBe(true)

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
    })

    it('trims whitespace from messages', async () => {
      mockSendMessage.mockResolvedValue({
        response: 'Response',
        metadata: { agent_role: 'kai', confidence: 0.95 },
      })

      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('  Hello Kai  ')
      })

      expect(mockSendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Hello Kai',
        }),
        expect.any(Object)
      )
    })

    it('does not send empty messages', async () => {
      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('')
      })

      expect(mockSendMessage).not.toHaveBeenCalled()
    })

    it('handles API errors gracefully', async () => {
      mockSendMessage.mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('Test message')
      })

      await waitFor(() => {
        expect(result.current.error).toBe('Network error')
      })

      // Should add error message to chat
      const lastMessage = result.current.messages[result.current.messages.length - 1]
      expect(lastMessage.role).toBe('assistant')
      expect(lastMessage.content).toContain('trouble connecting')
    })

    it('includes conversation history in API request', async () => {
      mockSendMessage.mockResolvedValue({
        response: 'Response 2',
        metadata: { agent_role: 'kai', confidence: 0.95 },
      })

      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('First message')
      })

      await act(async () => {
        await result.current.sendChatMessage('Second message')
      })

      expect(mockSendMessage).toHaveBeenLastCalledWith(
        expect.objectContaining({
          conversation_history: expect.arrayContaining([
            expect.objectContaining({
              role: 'user',
              content: 'First message',
            }),
          ]),
        }),
        expect.any(Object)
      )
    })
  })

  describe('clearConversation', () => {
    it('clears all messages', async () => {
      mockSendMessage.mockResolvedValue({
        response: 'Response',
        metadata: { agent_role: 'kai', confidence: 0.95 },
      })
      mockClearSession.mockResolvedValue(undefined)

      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('Test message')
      })

      expect(result.current.messages).toHaveLength(2)

      await act(async () => {
        await result.current.clearConversation()
      })

      expect(result.current.messages).toHaveLength(0)
      expect(mockClearSession).toHaveBeenCalledWith(userId)
    })

    it('clears error state', async () => {
      mockSendMessage.mockRejectedValue(new Error('Test error'))
      mockClearSession.mockResolvedValue(undefined)

      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('Test')
      })

      expect(result.current.error).toBeTruthy()

      await act(async () => {
        await result.current.clearConversation()
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('retryLastMessage', () => {
    it('retries the last user message', async () => {
      mockSendMessage
        .mockRejectedValueOnce(new Error('First attempt failed'))
        .mockResolvedValueOnce({
          response: 'Success',
          metadata: { agent_role: 'kai', confidence: 0.95 },
        })

      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('Test message')
      })

      expect(result.current.error).toBeTruthy()

      await act(async () => {
        await result.current.retryLastMessage()
      })

      await waitFor(() => {
        expect(result.current.error).toBeNull()
      })
    })

    it('removes failed messages before retrying', async () => {
      mockSendMessage
        .mockRejectedValueOnce(new Error('Failed'))
        .mockResolvedValueOnce({
          response: 'Success',
          metadata: { agent_role: 'kai', confidence: 0.95 },
        })

      const { result } = renderHook(() => useChat({ userId }))

      await act(async () => {
        await result.current.sendChatMessage('Test')
      })

      const messageCountBeforeRetry = result.current.messages.length

      await act(async () => {
        await result.current.retryLastMessage()
      })

      await waitFor(() => {
        // Should have same number of messages (removed error, added new response)
        expect(result.current.messages.length).toBe(messageCountBeforeRetry)
      })
    })
  })

  describe('Session Management', () => {
    it('creates new session', () => {
      const { result } = renderHook(() => useChat({ userId }))

      const initialSessionId = result.current.currentSession?.id

      act(() => {
        result.current.createNewSession()
      })

      expect(result.current.currentSession?.id).not.toBe(initialSessionId)
      expect(result.current.messages).toHaveLength(0)
    })

    it('loads existing session', () => {
      const session1 = {
        id: 'session-1',
        user_id: userId,
        messages: [
          {
            id: 'msg-1',
            role: 'user' as const,
            content: 'Session 1 message',
            timestamp: new Date(),
          },
        ],
        created_at: new Date(),
        updated_at: new Date(),
      }

      localStorage.setItem('kai-chat-sessions', JSON.stringify([session1]))

      const { result } = renderHook(() => useChat({ userId }))

      act(() => {
        result.current.loadSession('session-1')
      })

      expect(result.current.messages[0].content).toBe('Session 1 message')
    })

    it('deletes session', () => {
      const session1 = {
        id: 'session-1',
        user_id: userId,
        messages: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      localStorage.setItem('kai-chat-sessions', JSON.stringify([session1]))

      const { result } = renderHook(() => useChat({ userId }))

      act(() => {
        result.current.deleteSession('session-1')
      })

      expect(result.current.sessions).toHaveLength(0)
    })

    it('creates new session when deleting current session', () => {
      const session1 = {
        id: 'session-1',
        user_id: userId,
        messages: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      localStorage.setItem('kai-chat-sessions', JSON.stringify([session1]))
      localStorage.setItem('kai-current-session', 'session-1')

      const { result } = renderHook(() => useChat({ userId }))

      act(() => {
        result.current.deleteSession('session-1')
      })

      expect(result.current.currentSession?.id).not.toBe('session-1')
    })
  })

  describe('Auto-save', () => {
    it('saves sessions to localStorage when autoSave is true', async () => {
      mockSendMessage.mockResolvedValue({
        response: 'Response',
        metadata: { agent_role: 'kai', confidence: 0.95 },
      })

      const { result } = renderHook(() => useChat({ userId, autoSave: true }))

      await act(async () => {
        await result.current.sendChatMessage('Test message')
      })

      await waitFor(() => {
        const storedSessions = localStorage.getItem('kai-chat-sessions')
        expect(storedSessions).toBeTruthy()
      })
    })

    it('does not save when autoSave is false', async () => {
      mockSendMessage.mockResolvedValue({
        response: 'Response',
        metadata: { agent_role: 'kai', confidence: 0.95 },
      })

      const { result } = renderHook(() => useChat({ userId, autoSave: false }))

      await act(async () => {
        await result.current.sendChatMessage('Test message')
      })

      // Wait a bit to ensure no save occurs
      await new Promise(resolve => setTimeout(resolve, 100))

      const storedSessions = localStorage.getItem('kai-chat-sessions')
      expect(storedSessions).toBeNull()
    })
  })

  describe('Abort Controller', () => {
    it('cancels pending request when new message is sent', async () => {
      let firstCallAborted = false

      mockSendMessage.mockImplementation(async (_, options) => {
        return new Promise((resolve, reject) => {
          options?.signal?.addEventListener('abort', () => {
            firstCallAborted = true
            reject(new DOMException('Aborted', 'AbortError'))
          })

          setTimeout(() => {
            resolve({
              response: 'Response',
              metadata: { agent_role: 'kai', confidence: 0.95 },
            })
          }, 100)
        })
      })

      const { result } = renderHook(() => useChat({ userId }))

      act(() => {
        result.current.sendChatMessage('First message')
      })

      // Send second message before first completes
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 10))
        await result.current.sendChatMessage('Second message')
      })

      expect(firstCallAborted).toBe(true)
    })
  })
})
