# Kai Chat Interface - Quick Start Guide

## Prerequisites

1. Backend server running at `http://localhost:8000`
2. Node.js 18+ installed
3. Frontend dependencies installed

## Installation

```bash
cd /home/nix/projects/kai/frontend

# Install dependencies (already done)
npm install

# Create environment file (already done)
# .env.local contains: NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### 1. Start the Backend (in another terminal)

```bash
cd /home/nix/projects/kai/backend
# Follow backend startup instructions
# Backend should be running on http://localhost:8000
```

### 2. Start the Frontend

```bash
cd /home/nix/projects/kai/frontend
npm run dev
```

The application will start at: **http://localhost:3000**

### 3. Access the Chat Interface

1. Open browser to http://localhost:3000
2. Click **"Start Your Journey"** button
3. You'll be redirected to http://localhost:3000/chat
4. Start chatting with Kai!

## Testing the Interface

### Basic Flow

1. **First Visit**
   - See welcome screen with conversation starters
   - Type a message: "Hello, how are you?"
   - Press Enter or click send button
   - Watch typing indicator appear
   - See Kai's response

2. **Session Management**
   - Click "New Conversation" to start fresh
   - Previous conversations appear in sidebar
   - Click any conversation to reload it
   - Hover over conversation and click × to delete

3. **Features to Test**
   - **Markdown**: Try sending `**bold**` or `*italic*`
   - **Copy**: Hover over Kai's message and click copy icon
   - **Export**: Click download icon in header
   - **Theme**: Toggle light/dark mode in sidebar
   - **Mobile**: Resize window to see responsive design

### Connection Status

Look for the connection indicator in the top-right:
- 🟢 Green: Connected to backend
- 🔴 Red: Disconnected (backend not running)

If disconnected, you'll see a warning banner with retry option.

## File Structure Quick Reference

```
frontend/
├── app/
│   ├── chat/page.tsx          # Main chat interface
│   └── page.tsx               # Homepage with "Start Journey" button
│
├── components/chat/
│   ├── ChatMessage.tsx        # Individual message bubbles
│   ├── ChatInput.tsx          # Message input field
│   ├── ChatContainer.tsx      # Message list container
│   ├── ChatSidebar.tsx        # Conversation history
│   └── TypingIndicator.tsx    # Animated typing dots
│
├── hooks/
│   └── useChat.ts             # Chat state management
│
├── lib/
│   ├── api/chat.ts            # API client functions
│   └── types/chat.ts          # TypeScript types
│
└── .env.local                 # API URL configuration
```

## Common Issues & Solutions

### Issue: Cannot connect to backend

**Solution:**
1. Check backend is running: `curl http://localhost:8000/api/health`
2. Verify port 8000 is not blocked
3. Check CORS is configured in backend
4. Click "Retry connection" in the warning banner

### Issue: Messages not sending

**Solution:**
1. Check browser console for errors
2. Verify API URL in `.env.local`
3. Check network tab in browser DevTools
4. Try the retry button if it appears

### Issue: Sidebar not showing on mobile

**Solution:**
1. Click the hamburger menu (☰) in top-left
2. Sidebar should slide in from left
3. Click overlay or × to close

### Issue: Theme not persisting

**Solution:**
1. Check browser localStorage is enabled
2. Clear localStorage and try again
3. Theme preference is stored in localStorage

## Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line in message
- `Escape` - Close mobile sidebar (when open)

## API Endpoints Expected

Your backend should provide:

```
POST   /api/chat
GET    /api/chat/proactive/{user_id}
DELETE /api/chat/session/{user_id}
GET    /api/health
```

### Example Request to /api/chat

```json
{
  "user_id": "user-1234",
  "message": "Hello, how are you?",
  "conversation_history": [
    { "role": "user", "content": "Previous message" },
    { "role": "assistant", "content": "Previous response" }
  ]
}
```

### Example Response from /api/chat

```json
{
  "response": "I'm here to support you! How are you feeling today?",
  "metadata": {
    "agent_role": "kai",
    "confidence": 0.95,
    "wellness_insights": [
      {
        "category": "mood",
        "insight": "Checking in on emotional state",
        "severity": "info"
      }
    ]
  }
}
```

## Development Mode Features

- Hot reload on file changes
- React DevTools support
- TypeScript checking
- ESLint warnings in console

## Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, update to your production API URL:
```env
NEXT_PUBLIC_API_URL=https://api.kai-wellness.com
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Tips

1. **LocalStorage Size**: Conversations are auto-saved. Clear old sessions if needed.
2. **Network**: Use browser cache for static assets
3. **Images**: Icons are SVG for optimal performance
4. **Animations**: Hardware accelerated with CSS transforms

## Security Notes

- User ID is generated client-side (not secure for production)
- Messages are sent over HTTP (use HTTPS in production)
- LocalStorage is not encrypted
- Implement proper authentication before production use

## Next Steps

1. Test all features thoroughly
2. Check mobile responsiveness
3. Verify backend integration
4. Test error scenarios
5. Review accessibility
6. Plan for authentication
7. Consider WebSocket for real-time updates

## Support

For issues or questions:
1. Check browser console for errors
2. Review `CHAT_IMPLEMENTATION.md` for details
3. Review `FEATURES.md` for feature documentation
4. Check backend logs for API errors

---

Enjoy chatting with Kai! 💙🌊
