# Frontend Testing Suite

## Overview

Comprehensive testing suite for the Kai mental wellness platform frontend built with Jest and React Testing Library.

## Test Structure

```
__tests__/
├── components/
│   └── chat/
│       ├── ChatMessage.test.tsx      # Message display, markdown, metadata
│       ├── ChatInput.test.tsx        # Input field, sending, shortcuts
│       ├── ChatContainer.test.tsx    # Message list, empty state
│       └── TypingIndicator.test.tsx  # Loading indicator
├── hooks/
│   └── useChat.test.ts              # Chat state management, API calls
├── lib/
│   └── api/
│       └── chat.test.ts             # API client, error handling, retries
├── pages/
│   └── chat.test.tsx                # Full page integration tests
├── utils/
│   └── test-utils.tsx               # Custom render with providers
└── mocks/
    ├── handlers.ts                  # MSW API mock handlers
    └── server.ts                    # MSW server setup
```

## Test Coverage

### Components (4 files, 65+ tests)

#### ChatMessage.test.tsx
- ✅ Rendering user and assistant messages
- ✅ Markdown rendering for assistant messages
- ✅ Safety warning display
- ✅ Copy to clipboard functionality
- ✅ Metadata display (agent role, confidence)
- ✅ Wellness insights rendering
- ✅ Accessibility (ARIA labels, semantic HTML)
- ✅ Visual styling for different roles

#### ChatInput.test.tsx
- ✅ Input field rendering and placeholder
- ✅ User typing and character count
- ✅ Sending messages via button and Enter key
- ✅ Shift+Enter for new lines
- ✅ Input clearing after send
- ✅ Whitespace trimming
- ✅ Loading and disabled states
- ✅ Button state management
- ✅ Auto-resize and auto-focus
- ✅ Accessibility labels

#### ChatContainer.test.tsx
- ✅ Empty state with welcome message
- ✅ Suggestion cards display
- ✅ Message list rendering
- ✅ Typing indicator during loading
- ✅ Scrollable container
- ✅ Accessibility (ARIA roles, live regions)
- ✅ Layout and spacing
- ✅ Edge cases (single message, special characters)

#### TypingIndicator.test.tsx
- ✅ Component rendering
- ✅ "Kai is typing" text display
- ✅ Animation classes
- ✅ Accessibility

### Hooks (1 file, 40+ tests)

#### useChat.test.ts
- ✅ Initialization with empty messages
- ✅ Loading existing sessions from localStorage
- ✅ Sending messages and adding to state
- ✅ Loading state management
- ✅ Error handling and error messages
- ✅ Message trimming and validation
- ✅ Conversation history in API requests
- ✅ Clearing conversation
- ✅ Retrying failed messages
- ✅ Session management (create, load, delete)
- ✅ Auto-save to localStorage
- ✅ Abort controller for canceling requests

### API Client (1 file, 30+ tests)

#### chat.test.ts
- ✅ Sending messages successfully
- ✅ Including conversation history
- ✅ Handling safety warnings
- ✅ Error handling (4xx, 5xx status codes)
- ✅ Request abortion
- ✅ Retry logic with exponential backoff
- ✅ No retry on client errors or abort
- ✅ Malformed JSON handling
- ✅ Proactive check-in messages
- ✅ Clearing sessions
- ✅ Health check endpoint
- ✅ Request formatting (headers, body)

### Pages (1 file, 25+ tests)

#### chat.test.tsx
- ✅ Page rendering with header and footer
- ✅ API health check on mount
- ✅ Health status indicators
- ✅ Health warning display and dismissal
- ✅ Input disabled when API unhealthy
- ✅ Message display from hook
- ✅ Loading indicator
- ✅ Error message display and retry
- ✅ Sending messages
- ✅ Export conversation functionality
- ✅ Session management integration
- ✅ User ID generation and storage
- ✅ Accessibility (heading hierarchy, buttons)
- ✅ Layout structure

## Total Test Count

- **Component Tests**: ~65 tests
- **Hook Tests**: ~40 tests
- **API Tests**: ~30 tests
- **Page Tests**: ~25 tests
- **Total**: **160+ tests**

## Running Tests

### Standard Commands

```bash
# Run tests in watch mode
npm test

# Run tests once with coverage
npm run test:coverage

# Run tests in CI mode
npm run test:ci

# Debug tests
npm run test:debug
```

### Coverage Targets

- Lines: 80%
- Functions: 70%
- Branches: 70%
- Statements: 80%

## Key Testing Patterns

### 1. Custom Render with Providers

```typescript
import { render } from '@/__tests__/utils/test-utils'

// Automatically wraps components with ThemeProvider
render(<MyComponent />)
```

### 2. MSW API Mocking

```typescript
import { server } from '@/__tests__/mocks/server'

// Mock API responses
server.use(
  http.post('/api/chat', () => {
    return HttpResponse.json({ response: 'Test' })
  })
)
```

### 3. User Interactions

```typescript
import userEvent from '@testing-library/user-event'

const user = userEvent.setup()
await user.type(input, 'Hello')
await user.click(button)
```

### 4. Async Testing

```typescript
import { waitFor } from '@testing-library/react'

await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument()
})
```

## Test Utilities

### createMockMessage

Helper function to create mock message objects:

```typescript
const message = createMockMessage({
  role: 'assistant',
  content: 'Test message'
})
```

### createMockConversationHistory

Generate conversation history for testing:

```typescript
const history = createMockConversationHistory(5) // 5 messages
```

## Mocked APIs

All API endpoints are mocked using MSW:

- `POST /api/chat` - Send message
- `GET /api/chat/proactive/:userId` - Proactive check-in
- `DELETE /api/chat/session/:userId` - Clear session
- `GET /api/health` - Health check

## CI/CD Integration

Tests are configured for CI environments:

```bash
npm run test:ci
```

Features:
- No watch mode
- Coverage reporting
- Limited workers for stability
- Exit on completion

## Troubleshooting

### WSL Path Issues

If running in WSL and encountering UNC path errors, you may need to:

1. Run tests from a Windows terminal (PowerShell/CMD)
2. Use the WSL-native node installation
3. Or set up a proper jest configuration outside of Windows paths

### Module Resolution

The jest.config.js uses Next.js's createJestConfig which handles:
- Path aliases (@/ prefix)
- TypeScript transformation
- CSS/Image module mocking
- React component transformation

### Coverage Not Generating

Ensure all source files are in the collectCoverageFrom paths:
- `app/**/*.{js,jsx,ts,tsx}`
- `components/**/*.{js,jsx,ts,tsx}`
- `hooks/**/*.{js,jsx,ts,tsx}`
- `lib/**/*.{js,jsx,ts,tsx}`

## Next Steps

To extend the test suite:

1. **Add Component Tests**: Test new components as they're created
2. **Integration Tests**: Test component combinations
3. **E2E Tests**: Consider adding Playwright/Cypress for full flows
4. **Visual Regression**: Add screenshot testing with Percy/Chromatic
5. **Performance**: Add performance testing for heavy components

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [MSW Documentation](https://mswjs.io/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
