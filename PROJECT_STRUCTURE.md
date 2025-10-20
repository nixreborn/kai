# Kai - Project Structure

## Overview

Kai is an AI-driven mental wellness and journaling platform built with a modern tech stack and multi-agent architecture.

**Mission**: "Be the person you needed"

## Tech Stack

### Frontend
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS with dark/light mode
- **Theme**: next-themes for seamless theme switching
- **Port**: 3000

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **AI Framework**: PydanticAI
- **LLM**: OpenAI-compatible endpoint at `http://192.168.1.7:8000/v1`
- **Port**: 8000

### Multi-Agent System

#### Agents

1. **Kai (Main Agent)**
   - Role: Primary user interface agent
   - Personality: Warm, empathetic, trauma-informed
   - Features: Active listening, water therapy metaphors, proactive support
   - Location: `backend/src/agents/kai_agent.py`

2. **Guardrail Agent**
   - Role: Safety and content moderation
   - Features: Self-harm detection, crisis intervention, content filtering
   - Outputs: Safety levels (SAFE, WARNING, BLOCKED)
   - Location: `backend/src/agents/guardrail_agent.py`

3. **Genetic Counseling Agent**
   - Role: User trait mapping and AI personalization
   - Features: Personality analysis, communication style detection
   - Outputs: User traits with confidence scores
   - Location: `backend/src/agents/genetic_agent.py`

4. **Mental Wellness Agent**
   - Role: Pattern detection and proactive remediation
   - Features: Mood tracking, behavioral analysis, wellness insights
   - Outputs: Insights with severity levels and recommendations
   - Location: `backend/src/agents/wellness_agent.py`

#### Agent Orchestrator
- Coordinates multi-agent interactions
- Manages conversation flow
- Implements "Let me ask you a question" proactive feature
- Location: `backend/src/agents/orchestrator.py`

## Directory Structure

```
kai/
├── frontend/                    # Next.js frontend
│   ├── app/                     # App router pages
│   │   ├── layout.tsx           # Root layout with theme provider
│   │   ├── page.tsx             # Landing page
│   │   └── globals.css          # Global styles
│   ├── components/              # React components
│   │   ├── theme-provider.tsx   # Theme context provider
│   │   └── theme-toggle.tsx     # Light/dark mode toggle
│   ├── lib/                     # Utilities
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.ts
│
├── backend/                     # FastAPI backend
│   ├── src/
│   │   ├── agents/              # PydanticAI agents
│   │   │   ├── kai_agent.py     # Main Kai agent
│   │   │   ├── guardrail_agent.py
│   │   │   ├── genetic_agent.py
│   │   │   ├── wellness_agent.py
│   │   │   └── orchestrator.py  # Multi-agent coordinator
│   │   ├── api/                 # API routes
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   └── health.py        # Health checks
│   │   ├── core/                # Core configuration
│   │   │   ├── config.py        # Settings management
│   │   │   └── llm_client.py    # LLM client setup
│   │   ├── models/              # Pydantic models
│   │   │   └── agent_models.py  # Agent data models
│   │   └── main.py              # FastAPI application
│   ├── tests/                   # Test suite
│   ├── pyproject.toml           # Python dependencies
│   └── .env.example             # Environment template
│
├── docs/                        # Documentation
├── README.md                    # Main project README
└── PROJECT_STRUCTURE.md         # This file
```

## API Endpoints

### Chat API
- `POST /api/chat` - Send message to Kai
- `GET /api/chat/proactive/{user_id}` - Get proactive check-in
- `DELETE /api/chat/session/{user_id}` - Clear conversation history

### Health
- `GET /health` - Health check
- `GET /` - API info

## Development Workflow

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Runs on port 3000
```

### Backend Setup
```bash
cd backend
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your configuration
uvicorn src.main:app --reload  # Runs on port 8000
```

### Environment Configuration
Copy `backend/.env.example` to `backend/.env` and configure:
- LLM endpoint URL
- Database connection (when implemented)
- CORS origins
- Agent model settings

## Phase 1 Deliverables

✅ **Completed**:
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

🔄 **Next Steps** (Phase 1 continuation):
- [ ] Database integration (PostgreSQL)
- [ ] User authentication
- [ ] Journaling module
- [ ] Document/image upload
- [ ] Encryption layer
- [ ] Frontend chat interface
- [ ] Testing suite
- [ ] Deployment configuration

## Future Phases

See README.md for complete phase breakdown (Phases 2-5).

## Development Notes

### Agent Extensibility
New agents can be added by:
1. Creating agent in `backend/src/agents/`
2. Registering in `backend/src/agents/__init__.py`
3. Adding to orchestrator workflow in `orchestrator.py`
4. Updating `AgentRole` enum in `agent_models.py`

### Theme System
The frontend uses `next-themes` for seamless dark/light mode:
- System preference detection
- Manual toggle
- No flash on page load
- Tailwind `dark:` variants

### Safety System
All user messages pass through the Guardrail agent:
- SAFE: Normal processing
- WARNING: Flagged for monitoring
- BLOCKED: Crisis intervention response

### Proactive Remediation
Wellness agent analyzes patterns and triggers "Let me ask you a question":
- LOW severity: General wellness
- MEDIUM severity: Gentle check-in
- HIGH severity: Focused support question

## Contributing

This is a personal project in active development. Phase 1 implementation is underway.

## License

TBD
