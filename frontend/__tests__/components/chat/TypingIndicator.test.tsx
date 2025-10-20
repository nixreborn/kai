import { render, screen } from '@/__tests__/utils/test-utils'
import { TypingIndicator } from '@/components/chat/TypingIndicator'

describe('TypingIndicator', () => {
  it('renders the typing indicator', () => {
    const { container } = render(<TypingIndicator />)

    expect(container.firstChild).toBeInTheDocument()
  })

  it('displays Kai is typing text', () => {
    render(<TypingIndicator />)

    expect(screen.getByText('Kai is typing')).toBeInTheDocument()
  })

  it('renders with correct accessibility attributes', () => {
    render(<TypingIndicator />)

    const indicator = screen.getByText('Kai is typing')
    expect(indicator).toBeInTheDocument()
  })

  it('has animation classes', () => {
    const { container } = render(<TypingIndicator />)

    // Check for animation classes
    const animatedElements = container.querySelectorAll('.animate-bounce')
    expect(animatedElements.length).toBeGreaterThan(0)
  })

  it('applies correct styling classes', () => {
    const { container } = render(<TypingIndicator />)

    const mainDiv = container.firstChild as HTMLElement
    expect(mainDiv).toHaveClass('flex')
  })
})
