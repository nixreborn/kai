# Kai Chat Interface - Features Overview

## UI Components Created

### 1. ChatMessage Component
```
┌─────────────────────────────────────────────────────┐
│  [Avatar] User Message                              │
│           ┌──────────────────────────────┐          │
│           │ Hello, how are you?          │          │
│           └──────────────────────────────┘          │
│                                    9:30 AM [Copy]    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  [Kai] I'm here to support you! How are you         │
│  ┌──────────────────────────────────────────┐       │
│  │ I'm here to support you! **How are you   │       │
│  │ feeling today?** Let's talk about it.    │       │
│  └──────────────────────────────────────────┘       │
│  9:30 AM kai 95% [Copy]                             │
│  ┌────────────────────────────────────┐             │
│  │ Wellness Insights                  │             │
│  │ • Mood: Checking in on emotional   │             │
│  │   state                            │             │
│  └────────────────────────────────────┘             │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Distinct user/assistant styling with gradients
- Markdown rendering (bold, italic, lists, code, links)
- Copy message functionality
- Safety warning banners
- Wellness insights display
- Timestamp and metadata
- Accessibility labels

### 2. ChatInput Component
```
┌──────────────────────────────────────────────────┐
│  ┌────────────────────────────────────────┐ [📤] │
│  │ Share your thoughts with Kai...        │      │
│  │                                    123  │      │
│  └────────────────────────────────────────┘      │
│                                                   │
│  [Enter] to send • [Shift + Enter] for new line  │
└──────────────────────────────────────────────────┘
```

**Features:**
- Auto-resizing textarea (48px - 200px)
- Character counter
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Loading spinner when sending
- Gradient send button with hover effects
- Focus management
- Disabled state handling

### 3. ChatContainer Component
```
┌──────────────────────────────────────────────────┐
│                                                   │
│  Empty State:                                     │
│  ┌─────────────────────────────────────────────┐ │
│  │         [🌊]                                 │ │
│  │    Welcome to Kai                            │ │
│  │    Your mental wellness companion...         │ │
│  │                                              │ │
│  │  [💭] How are you feeling?                  │ │
│  │  [📝] I want to journal                     │ │
│  │  [🌊] Calming exercises                     │ │
│  │  [💡] Understand emotions                   │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  With Messages:                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ [Avatar] Message 1                          │ │
│  │ [Avatar] Message 2                          │ │
│  │ [Avatar] Message 3                          │ │
│  │ [•••] Typing indicator                      │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

**Features:**
- Auto-scroll to bottom on new messages
- Empty state with conversation starters
- Smooth scroll behavior
- Typing indicator display
- Responsive layout
- ARIA live region for accessibility

### 4. ChatSidebar Component
```
┌──────────────────────────┐
│ Kai                  [☀️] │
│ ┌──────────────────────┐ │
│ │ + New Conversation   │ │
│ └──────────────────────┘ │
│                          │
│ Your Profile             │
│ • communication: support │
│ • mood: positive         │
│                          │
│ Conversations            │
│ Today                    │
│ ┌──────────────────────┐ │
│ │ [💬] How are you...  │ │
│ │ Oct 20, 9:30 AM  [×] │ │
│ └──────────────────────┘ │
│ Yesterday                │
│ ┌──────────────────────┐ │
│ │ [💬] I'm feeling...  │ │
│ │ Oct 19, 3:45 PM  [×] │ │
│ └──────────────────────┘ │
│                          │
│ [📥] Export Conversation │
│ [⚙️] Settings            │
└──────────────────────────┘
```

**Features:**
- Conversation history grouped by date
- Session management (create, load, delete)
- User traits display
- Theme toggle
- Mobile responsive drawer
- Export conversation
- Settings access

### 5. TypingIndicator Component
```
┌──────────────┐
│ • • •        │  <- Animated wave effect
└──────────────┘
```

**Features:**
- Three animated dots
- Wave animation with staggered delays
- Aqua/ocean gradient colors
- Smooth transitions

## Page Layout

### Main Chat Page (/chat)
```
┌────────────────────────────────────────────────────────────────┐
│ [☰] Chat with Kai                    🟢 Connected [📥] [⚙️]   │
├────┬───────────────────────────────────────────────────────────┤
│    │                                                            │
│ S  │  ⚠️ Cannot connect to backend (if disconnected)           │
│ I  │                                                            │
│ D  │  ┌─────────────────────────────────────────────────┐     │
│ E  │  │                                                   │     │
│ B  │  │        Chat Messages Container                    │     │
│ A  │  │                                                   │     │
│ R  │  │  [Messages scroll here]                          │     │
│    │  │                                                   │     │
│    │  └─────────────────────────────────────────────────┘     │
│    │                                                            │
│    │  ┌─────────────────────────────────────────────────┐     │
│    │  │ Share your thoughts...                     [📤] │     │
│    │  └─────────────────────────────────────────────────┘     │
│    │                                                            │
│    │  Kai is an AI companion. For emergencies: Crisis 988     │
└────┴───────────────────────────────────────────────────────────┘
```

## Color Palette

### Aqua Theme (Primary)
- 50: #f0fdff (Lightest - backgrounds)
- 300: #5ae0fa (Light - hover states)
- 500: #00acd5 (Main - buttons, icons)
- 700: #006d91 (Dark - text)
- 950: #042f44 (Darkest - dark mode)

### Ocean Theme (Secondary)
- 50: #f0f9ff (Lightest)
- 400: #38bdf8 (Light)
- 500: #0ea5e9 (Main)
- 700: #0369a1 (Dark)
- 950: #082f49 (Darkest)

### Calm Theme (Accent)
- 50: #f0fdf9 (Lightest)
- 400: #2dd4b8 (Light)
- 500: #14b8a0 (Main)
- 700: #0b776a (Dark)
- 950: #032e2a (Darkest)

## Animations

1. **fade-in**: Smooth fade-in effect (0.3s)
2. **slide-up**: Slide up with fade (0.3s)
3. **pulse-slow**: Slow pulsing effect (3s)
4. **wave**: Wave animation for typing dots (2s)

## Responsive Design

### Desktop (lg+)
- Sidebar always visible (320px width)
- Chat area fills remaining space
- Comfortable spacing and padding

### Mobile (< lg)
- Sidebar slides in from left
- Hamburger menu button
- Overlay backdrop
- Touch-friendly sizing

## Accessibility Features

- ARIA labels on all interactive elements
- Keyboard navigation support
- Focus indicators
- Screen reader compatible
- Live regions for chat messages
- Semantic HTML structure
- High contrast support

## State Management

### useChat Hook
```typescript
const {
  messages,           // Array of Message objects
  isLoading,          // Boolean for API calls
  error,              // Error message string
  sendChatMessage,    // Function to send message
  clearConversation,  // Function to clear chat
  retryLastMessage,   // Function to retry failed message
  sessions,           // Array of ConversationSession
  currentSession,     // Current ConversationSession
  loadSession,        // Function to load session
  createNewSession,   // Function to create session
  deleteSession,      // Function to delete session
} = useChat({ userId, autoSave: true });
```

## API Integration

### Endpoints Used
- `POST /api/chat` - Send messages
- `GET /api/chat/proactive/{user_id}` - Get proactive check-ins
- `DELETE /api/chat/session/{user_id}` - Clear session
- `GET /api/health` - Health check

### Error Handling
- Automatic retry with exponential backoff
- User-friendly error messages
- Connection status indicator
- Retry button for failed messages

## Data Persistence

### LocalStorage Keys
- `kai-user-id`: Unique user identifier
- `kai-chat-sessions`: Array of conversation sessions
- `kai-current-session`: Current session ID

### Data Structure
```typescript
ConversationSession {
  id: string
  user_id: string
  messages: Message[]
  created_at: Date
  updated_at: Date
}

Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  metadata?: MessageMetadata
}
```

## Export Functionality

Users can export conversations as plain text files:
```
You: Hello, how are you?

Kai: I'm here to support you! How are you feeling today?

You: I'm feeling a bit anxious...

Kai: I understand. Let's talk about it...
```

---

Built with care for mental wellness 💙🌊
