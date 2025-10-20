import { render, screen, fireEvent, waitFor } from '@/__tests__/utils/test-utils'
import { ChatMessage } from '@/components/chat/ChatMessage'
import { Message } from '@/lib/types/chat'

describe('ChatMessage', () => {
  const baseMessage: Message = {
    id: 'msg-1',
    role: 'user',
    content: 'Hello, Kai!',
    timestamp: new Date('2024-01-01T12:00:00'),
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders user message correctly', () => {
      render(<ChatMessage message={baseMessage} />)

      expect(screen.getByText('Hello, Kai!')).toBeInTheDocument()
      expect(screen.getByRole('article')).toHaveAttribute('aria-label', 'Your message')
    })

    it('renders assistant message correctly', () => {
      const assistantMessage: Message = {
        ...baseMessage,
        id: 'msg-2',
        role: 'assistant',
        content: 'Hello! How can I help you today?',
      }

      render(<ChatMessage message={assistantMessage} />)

      expect(screen.getByText(/Hello! How can I help you today?/)).toBeInTheDocument()
      expect(screen.getByRole('article')).toHaveAttribute('aria-label', "Kai's message")
    })

    it('formats timestamp correctly', () => {
      render(<ChatMessage message={baseMessage} />)

      expect(screen.getByText('12:00 PM')).toBeInTheDocument()
    })

    it('renders markdown content for assistant messages', () => {
      const markdownMessage: Message = {
        ...baseMessage,
        role: 'assistant',
        content: 'Here is **bold** text and *italic* text.',
      }

      render(<ChatMessage message={markdownMessage} />)

      expect(screen.getByText('bold')).toBeInTheDocument()
      expect(screen.getByText('italic')).toBeInTheDocument()
    })

    it('renders plain text for user messages', () => {
      const userMessage: Message = {
        ...baseMessage,
        content: 'This is **not** markdown',
      }

      render(<ChatMessage message={userMessage} />)

      expect(screen.getByText('This is **not** markdown')).toBeInTheDocument()
    })
  })

  describe('Safety Warning', () => {
    it('displays safety warning when metadata includes it', () => {
      const warningMessage: Message = {
        ...baseMessage,
        role: 'assistant',
        metadata: {
          safety_warning: true,
          agent_role: 'kai',
        },
      }

      render(<ChatMessage message={warningMessage} />)

      expect(screen.getByText(/This message may contain sensitive content/)).toBeInTheDocument()
    })

    it('does not display safety warning when not present', () => {
      render(<ChatMessage message={baseMessage} />)

      expect(screen.queryByText(/This message may contain sensitive content/)).not.toBeInTheDocument()
    })
  })

  describe('Copy Functionality', () => {
    it('copies message content to clipboard when copy button is clicked', async () => {
      const writeText = jest.fn()
      Object.assign(navigator, {
        clipboard: {
          writeText,
        },
      })

      render(<ChatMessage message={baseMessage} />)

      const copyButton = screen.getByRole('button', { name: /copy message/i })
      fireEvent.click(copyButton)

      await waitFor(() => {
        expect(writeText).toHaveBeenCalledWith('Hello, Kai!')
      })
    })

    it('shows checkmark after successful copy', async () => {
      render(<ChatMessage message={baseMessage} />)

      const copyButton = screen.getByRole('button', { name: /copy message/i })
      fireEvent.click(copyButton)

      await waitFor(() => {
        expect(screen.getByTitle('Copy message')).toBeInTheDocument()
      })
    })
  })

  describe('Metadata Display', () => {
    it('displays agent role when provided', () => {
      const messageWithRole: Message = {
        ...baseMessage,
        role: 'assistant',
        metadata: {
          agent_role: 'wellness',
        },
      }

      render(<ChatMessage message={messageWithRole} />)

      expect(screen.getByText('wellness')).toBeInTheDocument()
    })

    it('displays confidence score when provided', () => {
      const messageWithConfidence: Message = {
        ...baseMessage,
        role: 'assistant',
        metadata: {
          confidence: 0.85,
          agent_role: 'kai',
        },
      }

      render(<ChatMessage message={messageWithConfidence} />)

      expect(screen.getByText('85%')).toBeInTheDocument()
    })

    it('does not display metadata for user messages', () => {
      const userMessage: Message = {
        ...baseMessage,
        metadata: {
          agent_role: 'kai',
          confidence: 0.95,
        },
      }

      render(<ChatMessage message={userMessage} />)

      expect(screen.queryByText('kai')).not.toBeInTheDocument()
      expect(screen.queryByText('95%')).not.toBeInTheDocument()
    })
  })

  describe('Wellness Insights', () => {
    it('displays wellness insights when provided', () => {
      const messageWithInsights: Message = {
        ...baseMessage,
        role: 'assistant',
        metadata: {
          agent_role: 'wellness',
          wellness_insights: [
            {
              category: 'Mood',
              insight: 'You seem to be in a positive mood today.',
            },
            {
              category: 'Sleep',
              insight: 'Consider maintaining a regular sleep schedule.',
            },
          ],
        },
      }

      render(<ChatMessage message={messageWithInsights} />)

      expect(screen.getByText('Wellness Insights')).toBeInTheDocument()
      expect(screen.getByText(/You seem to be in a positive mood today/)).toBeInTheDocument()
      expect(screen.getByText(/Consider maintaining a regular sleep schedule/)).toBeInTheDocument()
    })

    it('does not display wellness insights section when none provided', () => {
      render(<ChatMessage message={baseMessage} />)

      expect(screen.queryByText('Wellness Insights')).not.toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<ChatMessage message={baseMessage} />)

      expect(screen.getByRole('article')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /copy message/i })).toBeInTheDocument()
    })

    it('has proper link attributes for external links', () => {
      const messageWithLink: Message = {
        ...baseMessage,
        role: 'assistant',
        content: 'Check out [this link](https://example.com)',
      }

      render(<ChatMessage message={messageWithLink} />)

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })

  describe('Visual Styling', () => {
    it('applies correct styling for user messages', () => {
      render(<ChatMessage message={baseMessage} />)

      const article = screen.getByRole('article')
      expect(article).toHaveClass('flex-row-reverse')
    })

    it('applies correct styling for assistant messages', () => {
      const assistantMessage: Message = {
        ...baseMessage,
        role: 'assistant',
      }

      render(<ChatMessage message={assistantMessage} />)

      const article = screen.getByRole('article')
      expect(article).toHaveClass('flex-row')
    })
  })
})
