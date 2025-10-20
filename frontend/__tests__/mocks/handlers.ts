import { http, HttpResponse } from 'msw'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const handlers = [
  // POST /api/chat - Send message
  http.post(`${API_BASE_URL}/api/chat`, async ({ request }) => {
    const body = await request.json() as any

    // Simulate different responses based on message content
    if (body.message.toLowerCase().includes('error')) {
      return HttpResponse.json(
        { detail: 'Internal server error' },
        { status: 500 }
      )
    }

    if (body.message.toLowerCase().includes('safety')) {
      return HttpResponse.json({
        response: 'I understand you may be going through a difficult time. Let me help you with that.',
        metadata: {
          agent_role: 'kai',
          confidence: 0.95,
          safety_warning: true,
        },
      })
    }

    return HttpResponse.json({
      response: 'This is a test response from Kai.',
      metadata: {
        agent_role: 'kai',
        confidence: 0.95,
      },
    })
  }),

  // GET /api/chat/proactive/:userId - Get proactive check-in
  http.get(`${API_BASE_URL}/api/chat/proactive/:userId`, () => {
    return HttpResponse.json({
      response: 'How are you feeling today?',
      metadata: {
        agent_role: 'kai',
        confidence: 0.9,
        proactive: true,
      },
    })
  }),

  // DELETE /api/chat/session/:userId - Clear session
  http.delete(`${API_BASE_URL}/api/chat/session/:userId`, () => {
    return new HttpResponse(null, { status: 204 })
  }),

  // GET /api/health - Health check
  http.get(`${API_BASE_URL}/api/health`, () => {
    return HttpResponse.json({ status: 'ok' })
  }),
]

// Error handlers for specific test scenarios
export const errorHandlers = [
  http.post(`${API_BASE_URL}/api/chat`, () => {
    return HttpResponse.json(
      { detail: 'Server error' },
      { status: 500 }
    )
  }),
]

// Network error handlers
export const networkErrorHandlers = [
  http.post(`${API_BASE_URL}/api/chat`, () => {
    return HttpResponse.error()
  }),
]
