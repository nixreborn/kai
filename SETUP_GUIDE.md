# Kai - Setup and Development Guide

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- uv (Python package manager)
- OpenAI-compatible LLM endpoint running at `http://192.168.1.7:8000/v1`

### 1. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 2. Backend Setup

```bash
cd backend

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and configure your LLM endpoint

# Run the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- `http://localhost:8000` - API root
- `http://localhost:8000/docs` - Interactive API documentation
- `http://localhost:8000/redoc` - Alternative API documentation

## Environment Configuration

Edit `backend/.env` with your settings:

```env
# LLM Configuration (REQUIRED)
LLM_BASE_URL=http://192.168.1.7:8000/v1
LLM_API_KEY=optional-api-key
LLM_MODEL=default

# Frontend CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Agent Models (optional - defaults to LLM_MODEL)
KAI_AGENT_MODEL=default
GUARDRAIL_AGENT_MODEL=default
GENETIC_AGENT_MODEL=default
WELLNESS_AGENT_MODEL=default
```

## Testing the System

### 1. Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### 2. Test Chat API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "Hello, I'm feeling a bit anxious today"
  }'
```

Expected response:
```json
{
  "response": "Hi there. I hear that you're feeling anxious today...",
  "metadata": {
    "agent_role": "kai",
    "confidence": 0.85,
    "safety": "safe"
  }
}
```

### 3. Test Frontend

Visit `http://localhost:3000` and verify:
- Landing page loads
- Light/dark mode toggle works (top-right corner)
- "Start Your Journey" button is visible

## Architecture Overview

### Multi-Agent System Flow

```
User Message
     ↓
┌─────────────────────┐
│  Guardrail Agent    │  → Safety check (SAFE/WARNING/BLOCKED)
└─────────────────────┘
     ↓ (if safe)
┌─────────────────────┐
│   Kai Main Agent    │  → Generates empathetic response
└─────────────────────┘
     ↓ (in background)
┌─────────────────────┐
│  Genetic Agent      │  → Updates user trait profile
└─────────────────────┘
     ↓
┌─────────────────────┐
│  Wellness Agent     │  → Analyzes patterns & insights
└─────────────────────┘
     ↓
  Response to User
```

### Agent Responsibilities

**Kai (Main Agent)**
- Primary conversational interface
- Trauma-informed responses
- Water therapy metaphors
- Empathetic listening

**Guardrail Agent**
- Safety assessment
- Crisis detection
- Content moderation
- Emergency intervention

**Genetic Agent**
- Trait identification
- Communication style mapping
- Personalization engine
- Profile evolution

**Wellness Agent**
- Pattern detection
- Mood analysis
- Proactive prompts
- Wellness insights

## Development Commands

### Frontend

```bash
cd frontend

npm run dev          # Development server
npm run build        # Production build
npm run start        # Production server
npm run lint         # ESLint check
```

### Backend

```bash
cd backend

# Development
uvicorn src.main:app --reload

# Type checking
mypy src/

# Linting
ruff check src/

# Auto-fix
ruff check --fix src/

# Tests (when implemented)
pytest
pytest --cov=src
```

## Project Status

### ✅ Completed (Phase 1 - Part 1)

- [x] Next.js frontend with light/dark mode
- [x] FastAPI backend structure
- [x] OpenAI-compatible LLM integration
- [x] PydanticAI multi-agent system
- [x] Kai main agent
- [x] Guardrail agent
- [x] Genetic counseling agent
- [x] Mental wellness agent
- [x] Agent orchestration system
- [x] Chat API endpoints

### 📋 TODO (Phase 1 - Part 2)

**High Priority:**
- [ ] Database integration (PostgreSQL)
- [ ] User authentication system
- [ ] Journaling module backend
- [ ] Encryption and privacy layer
- [ ] Frontend chat interface
- [ ] Frontend authentication pages

**Medium Priority:**
- [ ] Document/image upload system
- [ ] Frontend journaling interface
- [ ] Logging and analytics (TRACE)
- [ ] Testing suite (backend)
- [ ] Testing suite (frontend)

**Low Priority:**
- [ ] Docker deployment configuration
- [ ] Mobile app foundation (React Native)

## API Documentation

### Endpoints

**Health Check**
```
GET /health
```

**Chat**
```
POST /api/chat
{
  "user_id": "string",
  "message": "string",
  "conversation_history": [...]  // optional
}
```

**Proactive Check-in**
```
GET /api/chat/proactive/{user_id}
```

**Clear Session**
```
DELETE /api/chat/session/{user_id}
```

## Troubleshooting

### Issue: LLM connection fails

**Solution**: Verify your LLM endpoint is running:
```bash
curl http://192.168.1.7:8000/v1/models
```

### Issue: Frontend can't connect to backend

**Solution**: Check CORS settings in `backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Issue: Import errors in backend

**Solution**: Ensure you're in the virtual environment:
```bash
cd backend
source .venv/bin/activate
which python  # Should show .venv/bin/python
```

## Next Steps

1. **Database Setup** - Install PostgreSQL and create migrations
2. **Authentication** - Implement JWT-based auth system
3. **Chat UI** - Build interactive chat interface
4. **Journaling** - Create journal entry system
5. **Testing** - Write comprehensive test suite

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)

## Support

This is a Phase 1 development project. For issues or questions, refer to the project documentation or Archon project board.

---

**Mission**: "Be the person you needed"
