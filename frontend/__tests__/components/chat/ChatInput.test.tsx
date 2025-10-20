import { render, screen, fireEvent, waitFor } from '@/__tests__/utils/test-utils'
import { ChatInput } from '@/components/chat/ChatInput'
import userEvent from '@testing-library/user-event'

describe('ChatInput', () => {
  const mockOnSend = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders input field with default placeholder', () => {
      render(<ChatInput onSend={mockOnSend} />)

      expect(screen.getByPlaceholderText('Share your thoughts with Kai...')).toBeInTheDocument()
    })

    it('renders with custom placeholder', () => {
      render(<ChatInput onSend={mockOnSend} placeholder="Custom placeholder" />)

      expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument()
    })

    it('renders send button', () => {
      render(<ChatInput onSend={mockOnSend} />)

      expect(screen.getByRole('button', { name: /send message/i })).toBeInTheDocument()
    })

    it('renders keyboard shortcut hints', () => {
      render(<ChatInput onSend={mockOnSend} />)

      expect(screen.getByText('Enter')).toBeInTheDocument()
      expect(screen.getByText('Shift + Enter')).toBeInTheDocument()
    })
  })

  describe('User Input', () => {
    it('allows typing in the textarea', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Hello Kai')

      expect(textarea).toHaveValue('Hello Kai')
    })

    it('displays character count when typing', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Hello')

      expect(screen.getByText('5')).toBeInTheDocument()
    })

    it('does not display character count when input is empty', () => {
      render(<ChatInput onSend={mockOnSend} />)

      expect(screen.queryByText(/^\d+$/)).not.toBeInTheDocument()
    })
  })

  describe('Sending Messages', () => {
    it('calls onSend when send button is clicked', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Test message')

      const sendButton = screen.getByRole('button', { name: /send message/i })
      await user.click(sendButton)

      expect(mockOnSend).toHaveBeenCalledWith('Test message')
    })

    it('calls onSend when Enter is pressed', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Test message{Enter}')

      expect(mockOnSend).toHaveBeenCalledWith('Test message')
    })

    it('does not call onSend when Shift+Enter is pressed', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Line 1{Shift>}{Enter}{/Shift}Line 2')

      expect(mockOnSend).not.toHaveBeenCalled()
      expect(textarea).toHaveValue('Line 1\nLine 2')
    })

    it('clears input after sending', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Test message')
      await user.click(screen.getByRole('button', { name: /send message/i }))

      expect(textarea).toHaveValue('')
    })

    it('trims whitespace from messages', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, '  Test message  ')
      await user.click(screen.getByRole('button', { name: /send message/i }))

      expect(mockOnSend).toHaveBeenCalledWith('Test message')
    })

    it('does not send empty messages', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const sendButton = screen.getByRole('button', { name: /send message/i })
      await user.click(sendButton)

      expect(mockOnSend).not.toHaveBeenCalled()
    })

    it('does not send whitespace-only messages', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, '   ')
      await user.click(screen.getByRole('button', { name: /send message/i }))

      expect(mockOnSend).not.toHaveBeenCalled()
    })
  })

  describe('Loading State', () => {
    it('disables input and button when loading', () => {
      render(<ChatInput onSend={mockOnSend} isLoading={true} />)

      const textarea = screen.getByRole('textbox')
      const sendButton = screen.getByRole('button', { name: /send message/i })

      expect(textarea).toBeDisabled()
      expect(sendButton).toBeDisabled()
    })

    it('shows loading spinner when loading', () => {
      render(<ChatInput onSend={mockOnSend} isLoading={true} />)

      // The Loader2 icon should be present (has animate-spin class)
      const sendButton = screen.getByRole('button', { name: /send message/i })
      expect(sendButton.querySelector('.animate-spin')).toBeInTheDocument()
    })

    it('does not call onSend when loading', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} isLoading={true} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Test message')

      const sendButton = screen.getByRole('button', { name: /send message/i })
      await user.click(sendButton)

      expect(mockOnSend).not.toHaveBeenCalled()
    })
  })

  describe('Disabled State', () => {
    it('disables input and button when disabled prop is true', () => {
      render(<ChatInput onSend={mockOnSend} disabled={true} />)

      const textarea = screen.getByRole('textbox')
      const sendButton = screen.getByRole('button', { name: /send message/i })

      expect(textarea).toBeDisabled()
      expect(sendButton).toBeDisabled()
    })

    it('does not call onSend when disabled', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} disabled={true} />)

      const sendButton = screen.getByRole('button', { name: /send message/i })
      await user.click(sendButton)

      expect(mockOnSend).not.toHaveBeenCalled()
    })
  })

  describe('Button State', () => {
    it('disables send button when input is empty', () => {
      render(<ChatInput onSend={mockOnSend} />)

      const sendButton = screen.getByRole('button', { name: /send message/i })
      expect(sendButton).toBeDisabled()
    })

    it('enables send button when input has text', async () => {
      const user = userEvent.setup()
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Test')

      const sendButton = screen.getByRole('button', { name: /send message/i })
      expect(sendButton).not.toBeDisabled()
    })
  })

  describe('Auto-resize', () => {
    it('focuses textarea on mount', () => {
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      expect(textarea).toHaveFocus()
    })

    it('has correct min and max height styles', () => {
      render(<ChatInput onSend={mockOnSend} />)

      const textarea = screen.getByRole('textbox')
      expect(textarea).toHaveStyle({
        minHeight: '48px',
        maxHeight: '200px',
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<ChatInput onSend={mockOnSend} />)

      expect(screen.getByLabelText('Message input')).toBeInTheDocument()
      expect(screen.getByLabelText('Send message')).toBeInTheDocument()
    })

    it('has proper title attributes', () => {
      render(<ChatInput onSend={mockOnSend} />)

      const sendButton = screen.getByRole('button', { name: /send message/i })
      expect(sendButton).toHaveAttribute('title', 'Send message (Enter)')
    })
  })
})
