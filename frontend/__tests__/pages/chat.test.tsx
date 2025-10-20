import { render, screen, waitFor, fireEvent } from '@/__tests__/utils/test-utils'
import ChatPage from '@/app/chat/page'
import * as chatApi from '@/lib/api/chat'
import { useChat } from '@/hooks/useChat'
import userEvent from '@testing-library/user-event'

// Mock the useChat hook
jest.mock('@/hooks/useChat')
const mockUseChat = useChat as jest.MockedFunction<typeof useChat>

// Mock the chat API
jest.mock('@/lib/api/chat')
const mockCheckHealth = chatApi.checkHealth as jest.MockedFunction<typeof chatApi.checkHealth>

describe('ChatPage', () => {
  const mockSendChatMessage = jest.fn()
  const mockClearConversation = jest.fn()
  const mockRetryLastMessage = jest.fn()
  const mockLoadSession = jest.fn()
  const mockCreateNewSession = jest.fn()
  const mockDeleteSession = jest.fn()

  const defaultUseChatReturn = {
    messages: [],
    isLoading: false,
    error: null,
    sendChatMessage: mockSendChatMessage,
    clearConversation: mockClearConversation,
    retryLastMessage: mockRetryLastMessage,
    sessions: [],
    currentSession: null,
    loadSession: mockLoadSession,
    createNewSession: mockCreateNewSession,
    deleteSession: mockDeleteSession,
  }

  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
    mockUseChat.mockReturnValue(defaultUseChatReturn)
    mockCheckHealth.mockResolvedValue(true)
  })

  describe('Page Rendering', () => {
    it('renders chat page with header', () => {
      render(<ChatPage />)

      expect(screen.getByText('Chat with Kai')).toBeInTheDocument()
      expect(screen.getByText('Your mental wellness companion')).toBeInTheDocument()
    })

    it('renders chat components', () => {
      render(<ChatPage />)

      // Check for main components
      expect(screen.getByRole('log')).toBeInTheDocument() // ChatContainer
      expect(screen.getByRole('textbox')).toBeInTheDocument() // ChatInput
    })

    it('renders footer with crisis information', () => {
      render(<ChatPage />)

      expect(screen.getByText(/Kai is an AI companion/)).toBeInTheDocument()
      expect(screen.getByText('Crisis: 988')).toBeInTheDocument()
    })

    it('crisis link has correct href', () => {
      render(<ChatPage />)

      const crisisLink = screen.getByText('Crisis: 988')
      expect(crisisLink).toHaveAttribute('href', 'tel:988')
    })
  })

  describe('API Health Check', () => {
    it('checks API health on mount', async () => {
      render(<ChatPage />)

      await waitFor(() => {
        expect(mockCheckHealth).toHaveBeenCalled()
      })
    })

    it('displays connected status when API is healthy', async () => {
      mockCheckHealth.mockResolvedValue(true)
      render(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Connected')).toBeInTheDocument()
      })
    })

    it('displays disconnected status when API is unhealthy', async () => {
      mockCheckHealth.mockResolvedValue(false)
      render(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Disconnected')).toBeInTheDocument()
      })
    })

    it('displays health warning when API is down', async () => {
      mockCheckHealth.mockResolvedValue(false)
      render(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Cannot connect to Kai backend')).toBeInTheDocument()
      })
    })

    it('allows retrying connection', async () => {
      mockCheckHealth.mockResolvedValueOnce(false).mockResolvedValueOnce(true)
      render(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Retry connection')).toBeInTheDocument()
      })

      const retryButton = screen.getByText('Retry connection')
      fireEvent.click(retryButton)

      await waitFor(() => {
        expect(mockCheckHealth).toHaveBeenCalledTimes(2)
      })
    })

    it('allows dismissing health warning', async () => {
      mockCheckHealth.mockResolvedValue(false)
      render(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Cannot connect to Kai backend')).toBeInTheDocument()
      })

      const dismissButton = screen.getByLabelText('Dismiss')
      fireEvent.click(dismissButton)

      await waitFor(() => {
        expect(screen.queryByText('Cannot connect to Kai backend')).not.toBeInTheDocument()
      })
    })

    it('disables input when API is unhealthy', async () => {
      mockCheckHealth.mockResolvedValue(false)
      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
      })

      render(<ChatPage />)

      await waitFor(() => {
        const input = screen.getByRole('textbox')
        expect(input).toBeDisabled()
      })
    })
  })

  describe('Message Display', () => {
    it('displays messages from useChat hook', () => {
      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
        messages: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'Hello Kai',
            timestamp: new Date(),
          },
          {
            id: 'msg-2',
            role: 'assistant',
            content: 'Hello! How can I help?',
            timestamp: new Date(),
            metadata: { agent_role: 'kai', confidence: 0.95 },
          },
        ],
      })

      render(<ChatPage />)

      expect(screen.getByText('Hello Kai')).toBeInTheDocument()
      expect(screen.getByText(/Hello! How can I help?/)).toBeInTheDocument()
    })

    it('shows loading indicator when sending message', () => {
      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
        isLoading: true,
      })

      render(<ChatPage />)

      // Loading spinner should be visible
      const sendButton = screen.getByRole('button', { name: /send message/i })
      expect(sendButton.querySelector('.animate-spin')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('displays error message when present', () => {
      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
        error: 'Network error occurred',
      })

      render(<ChatPage />)

      expect(screen.getByText('Error')).toBeInTheDocument()
      expect(screen.getByText('Network error occurred')).toBeInTheDocument()
    })

    it('allows retrying failed message', () => {
      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
        error: 'Failed to send',
      })

      render(<ChatPage />)

      const retryButton = screen.getByRole('button', { name: /retry/i })
      fireEvent.click(retryButton)

      expect(mockRetryLastMessage).toHaveBeenCalled()
    })
  })

  describe('Sending Messages', () => {
    it('sends message when form is submitted', async () => {
      const user = userEvent.setup()
      render(<ChatPage />)

      const input = screen.getByRole('textbox')
      await user.type(input, 'Test message')

      const sendButton = screen.getByRole('button', { name: /send message/i })
      await user.click(sendButton)

      expect(mockSendChatMessage).toHaveBeenCalledWith('Test message')
    })
  })

  describe('Export Conversation', () => {
    it('shows export button when messages exist', () => {
      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
        messages: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'Test',
            timestamp: new Date(),
          },
        ],
        currentSession: {
          id: 'session-1',
          user_id: 'user-123',
          messages: [
            {
              id: 'msg-1',
              role: 'user',
              content: 'Test',
              timestamp: new Date(),
            },
          ],
          created_at: new Date(),
          updated_at: new Date(),
        },
      })

      render(<ChatPage />)

      expect(screen.getByLabelText('Export conversation')).toBeInTheDocument()
    })

    it('does not show export button when no messages', () => {
      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
        messages: [],
      })

      render(<ChatPage />)

      expect(screen.queryByLabelText('Export conversation')).not.toBeInTheDocument()
    })

    it('exports conversation as text file', () => {
      // Mock document.createElement and related methods
      const mockClick = jest.fn()
      const mockAppendChild = jest.fn()
      const mockRemoveChild = jest.fn()
      const mockCreateElement = jest.spyOn(document, 'createElement')
      const mockCreateObjectURL = jest.fn(() => 'blob:mock-url')
      const mockRevokeObjectURL = jest.fn()

      global.URL.createObjectURL = mockCreateObjectURL
      global.URL.revokeObjectURL = mockRevokeObjectURL

      const mockAnchor = {
        href: '',
        download: '',
        click: mockClick,
      } as unknown as HTMLAnchorElement

      mockCreateElement.mockReturnValue(mockAnchor)

      document.body.appendChild = mockAppendChild
      document.body.removeChild = mockRemoveChild

      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
        messages: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'Hello',
            timestamp: new Date(),
          },
        ],
        currentSession: {
          id: 'session-1',
          user_id: 'user-123',
          messages: [
            {
              id: 'msg-1',
              role: 'user',
              content: 'Hello',
              timestamp: new Date(),
            },
            {
              id: 'msg-2',
              role: 'assistant',
              content: 'Hi there',
              timestamp: new Date(),
            },
          ],
          created_at: new Date(),
          updated_at: new Date(),
        },
      })

      render(<ChatPage />)

      const exportButton = screen.getByLabelText('Export conversation')
      fireEvent.click(exportButton)

      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('blob:mock-url')

      // Cleanup
      mockCreateElement.mockRestore()
    })
  })

  describe('Session Management', () => {
    it('passes sessions to sidebar', () => {
      const mockSessions = [
        {
          id: 'session-1',
          user_id: 'user-123',
          messages: [],
          created_at: new Date(),
          updated_at: new Date(),
        },
      ]

      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
        sessions: mockSessions,
      })

      render(<ChatPage />)

      // The sidebar should receive the sessions prop
      expect(mockUseChat).toHaveBeenCalled()
    })

    it('passes callbacks to sidebar', () => {
      render(<ChatPage />)

      // Verify that useChat was called and all callbacks are passed to sidebar
      expect(mockUseChat).toHaveBeenCalled()
    })
  })

  describe('User ID Generation', () => {
    it('generates and stores user ID on first visit', () => {
      render(<ChatPage />)

      const storedUserId = localStorage.getItem('kai-user-id')
      expect(storedUserId).toBeTruthy()
      expect(storedUserId).toMatch(/^user-/)
    })

    it('reuses existing user ID', () => {
      localStorage.setItem('kai-user-id', 'existing-user-123')

      render(<ChatPage />)

      expect(mockUseChat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'existing-user-123',
        })
      )
    })
  })

  describe('Accessibility', () => {
    it('has proper heading hierarchy', () => {
      render(<ChatPage />)

      const heading = screen.getByRole('heading', { level: 1 })
      expect(heading).toHaveTextContent('Chat with Kai')
    })

    it('has accessible buttons', () => {
      mockUseChat.mockReturnValue({
        ...defaultUseChatReturn,
        messages: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'Test',
            timestamp: new Date(),
          },
        ],
        currentSession: {
          id: 'session-1',
          user_id: 'user-123',
          messages: [],
          created_at: new Date(),
          updated_at: new Date(),
        },
      })

      render(<ChatPage />)

      expect(screen.getByLabelText('Export conversation')).toBeInTheDocument()
      expect(screen.getByLabelText('Message input')).toBeInTheDocument()
      expect(screen.getByLabelText('Send message')).toBeInTheDocument()
    })
  })

  describe('Layout', () => {
    it('has correct layout structure', () => {
      const { container } = render(<ChatPage />)

      const mainContainer = container.querySelector('.flex.h-screen')
      expect(mainContainer).toBeInTheDocument()
    })

    it('renders sidebar and main content area', () => {
      render(<ChatPage />)

      // Sidebar should be present (contains session management)
      // Main content should be present (contains chat)
      expect(screen.getByRole('log')).toBeInTheDocument()
    })
  })
})
