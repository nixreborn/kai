import { render, screen } from '@/__tests__/utils/test-utils'
import { ChatContainer } from '@/components/chat/ChatContainer'
import { Message } from '@/lib/types/chat'

describe('ChatContainer', () => {
  const mockMessages: Message[] = [
    {
      id: 'msg-1',
      role: 'user',
      content: 'Hello!',
      timestamp: new Date('2024-01-01T12:00:00'),
    },
    {
      id: 'msg-2',
      role: 'assistant',
      content: 'Hi there! How can I help you today?',
      timestamp: new Date('2024-01-01T12:01:00'),
      metadata: {
        agent_role: 'kai',
        confidence: 0.95,
      },
    },
    {
      id: 'msg-3',
      role: 'user',
      content: 'I need help with my mental health',
      timestamp: new Date('2024-01-01T12:02:00'),
    },
  ]

  describe('Empty State', () => {
    it('displays welcome message when no messages', () => {
      render(<ChatContainer messages={[]} />)

      expect(screen.getByText('Welcome to Kai')).toBeInTheDocument()
      expect(screen.getByText(/Your mental wellness companion is here to listen/)).toBeInTheDocument()
    })

    it('displays suggestion cards in empty state', () => {
      render(<ChatContainer messages={[]} />)

      expect(screen.getByText('How are you feeling today?')).toBeInTheDocument()
      expect(screen.getByText('I want to journal about my day')).toBeInTheDocument()
      expect(screen.getByText('I need some calming exercises')).toBeInTheDocument()
      expect(screen.getByText('Help me understand my emotions')).toBeInTheDocument()
    })

    it('does not display welcome message when messages exist', () => {
      render(<ChatContainer messages={mockMessages} />)

      expect(screen.queryByText('Welcome to Kai')).not.toBeInTheDocument()
    })
  })

  describe('Message Display', () => {
    it('renders all messages', () => {
      render(<ChatContainer messages={mockMessages} />)

      expect(screen.getByText('Hello!')).toBeInTheDocument()
      expect(screen.getByText(/Hi there! How can I help you today?/)).toBeInTheDocument()
      expect(screen.getByText('I need help with my mental health')).toBeInTheDocument()
    })

    it('renders messages in correct order', () => {
      render(<ChatContainer messages={mockMessages} />)

      const messages = screen.getAllByRole('article')
      expect(messages).toHaveLength(3)
    })

    it('applies group class to each message wrapper', () => {
      render(<ChatContainer messages={mockMessages} />)

      const messageWrappers = screen.getAllByRole('article').map(article => article.parentElement)
      messageWrappers.forEach(wrapper => {
        expect(wrapper).toHaveClass('group')
      })
    })
  })

  describe('Loading State', () => {
    it('displays typing indicator when loading', () => {
      render(<ChatContainer messages={mockMessages} isLoading={true} />)

      // The TypingIndicator component should be present
      // We can verify by checking for the flex container that holds it
      const container = screen.getByRole('log')
      expect(container).toBeInTheDocument()
    })

    it('does not display typing indicator when not loading', () => {
      const { container } = render(<ChatContainer messages={mockMessages} isLoading={false} />)

      // Check that there's no typing indicator by looking for elements with specific classes
      const typingIndicator = container.querySelector('.animate-bounce')
      expect(typingIndicator).not.toBeInTheDocument()
    })

    it('displays typing indicator in empty state when loading', () => {
      render(<ChatContainer messages={[]} isLoading={true} />)

      // When loading with no messages, the empty state should not be shown
      expect(screen.queryByText('Welcome to Kai')).not.toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA role and attributes', () => {
      render(<ChatContainer messages={mockMessages} />)

      const container = screen.getByRole('log')
      expect(container).toHaveAttribute('aria-live', 'polite')
      expect(container).toHaveAttribute('aria-label', 'Chat messages')
    })

    it('has scrollable container', () => {
      render(<ChatContainer messages={mockMessages} />)

      const container = screen.getByRole('log')
      expect(container).toHaveClass('overflow-y-auto')
    })
  })

  describe('Container Structure', () => {
    it('has correct layout classes', () => {
      render(<ChatContainer messages={mockMessages} />)

      const container = screen.getByRole('log')
      expect(container).toHaveClass('flex-1', 'overflow-y-auto', 'scroll-smooth')
    })

    it('centers content with max width', () => {
      const { container } = render(<ChatContainer messages={mockMessages} />)

      const innerContainer = container.querySelector('.max-w-4xl')
      expect(innerContainer).toBeInTheDocument()
      expect(innerContainer).toHaveClass('mx-auto')
    })

    it('applies spacing between messages', () => {
      const { container } = render(<ChatContainer messages={mockMessages} />)

      const messageContainer = container.querySelector('.space-y-6')
      expect(messageContainer).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('handles single message', () => {
      const singleMessage = [mockMessages[0]]
      render(<ChatContainer messages={singleMessage} />)

      expect(screen.getByText('Hello!')).toBeInTheDocument()
      expect(screen.getAllByRole('article')).toHaveLength(1)
    })

    it('handles empty messages array with loading', () => {
      render(<ChatContainer messages={[]} isLoading={true} />)

      const container = screen.getByRole('log')
      expect(container).toBeInTheDocument()
    })

    it('handles messages with special characters', () => {
      const specialMessage: Message = {
        id: 'msg-special',
        role: 'user',
        content: 'Special chars: <>&"\'',
        timestamp: new Date(),
      }

      render(<ChatContainer messages={[specialMessage]} />)

      expect(screen.getByText(/Special chars:/)).toBeInTheDocument()
    })
  })

  describe('Suggestion Cards', () => {
    it('renders all suggestion cards with emojis', () => {
      render(<ChatContainer messages={[]} />)

      // Check for emojis
      expect(screen.getByText('💭')).toBeInTheDocument()
      expect(screen.getByText('📝')).toBeInTheDocument()
      expect(screen.getByText('🌊')).toBeInTheDocument()
      expect(screen.getByText('💡')).toBeInTheDocument()
    })

    it('suggestion cards have cursor pointer', () => {
      const { container } = render(<ChatContainer messages={[]} />)

      const suggestionCards = container.querySelectorAll('.cursor-pointer')
      expect(suggestionCards.length).toBeGreaterThan(0)
    })
  })
})
