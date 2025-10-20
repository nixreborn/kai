# 🌊 Kai - AI-Driven Mental Wellness Platform

**Mission**: "Be the person you needed"

Kai is a trauma-informed mental wellness companion powered by a sophisticated multi-agent AI system. Built with Next.js, FastAPI, and PydanticAI, Kai provides personalized journaling, proactive emotional support, and wellness insights through empathetic AI interactions.

## ✨ Features

### Core Capabilities (Phase 1)
- **🤖 Multi-Agent AI System**: Four specialized AI agents working together
  - **Kai (Main Agent)**: Warm, empathetic conversational companion
  - **Guardrail Agent**: Safety monitoring and crisis detection
  - **Genetic Agent**: Personality mapping and AI personalization
  - **Wellness Agent**: Pattern detection and proactive support

- **💬 Intelligent Conversations**: Trauma-informed responses with active listening
- **🌊 Water Therapy Integration**: Calming aqua-themed metaphors and mindfulness
- **🛡️ Safety First**: Built-in crisis detection and intervention
- **🎨 Beautiful UI**: Next.js frontend with seamless light/dark mode
- **🔒 Privacy-Focused**: End-to-end encryption (coming soon)

### Planned Features (Future Phases)
- 📔 AI-powered journaling with intelligent prompts
- 📊 Mood tracking and behavioral analysis
- 🔔 Proactive check-ins and wellness reminders
- 🎮 Gamification and progress tracking
- 📱 Mobile apps (iOS & Android)
- 🤝 Optional human coach integration

## 🏗️ Architecture

### Tech Stack

**Frontend**
- Next.js 15 (App Router)
- TypeScript 5
- Tailwind CSS
- next-themes (dark mode)

**Backend**
- FastAPI (Python 3.11+)
- PydanticAI (multi-agent framework)
- OpenAI-compatible LLM endpoint
- PostgreSQL (planned)

**AI/LLM**
- OpenAI-compatible endpoint at `http://192.168.1.7:8000/v1`
- Supports any OpenAI API-compatible model

### Multi-Agent Flow

```
User Input
    ↓
┌──────────────────┐
│ Guardrail Agent  │ → Safety Check (SAFE/WARNING/BLOCKED)
└──────────────────┘
    ↓ if safe
┌──────────────────┐
│  Kai Main Agent  │ → Empathetic Response
└──────────────────┘
    ↓ background
┌──────────────────┐
│ Genetic Agent    │ → Update User Profile
└──────────────────┘
    ↓
┌──────────────────┐
│ Wellness Agent   │ → Analyze Patterns
└──────────────────┘
    ↓
Proactive Insights
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

**One-command setup:**
```bash
./scripts/start-dev.sh
```

This starts the entire platform:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- PostgreSQL database

**Prerequisites:**
- Docker & Docker Compose
- 4GB RAM
- Ports 3000, 5432, 8000 available

See [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) for detailed Docker instructions.

### Option 2: Local Development

**Prerequisites:**
- Node.js 18+
- Python 3.11+
- uv (Python package manager)
- OpenAI-compatible LLM endpoint

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000`

**Backend Setup:**
```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your LLM endpoint
uvicorn src.main:app --reload
```
API docs: `http://localhost:8000/docs`

## 📖 Documentation

- [Docker Quick Start](DOCKER_QUICK_START.md) - Get running in minutes with Docker
- [Deployment Guide](DEPLOYMENT.md) - Comprehensive deployment documentation
- [Setup Guide](SETUP_GUIDE.md) - Detailed installation and configuration
- [Project Structure](PROJECT_STRUCTURE.md) - Architecture and code organization
- API Documentation - Available at `/docs` when backend is running

## 🎯 Development Status

### ✅ Phase 1 - Core Infrastructure (9/22 tasks complete - 41%)

**Completed:**
- [x] Next.js frontend with light/dark mode
- [x] FastAPI backend structure
- [x] OpenAI-compatible LLM integration
- [x] PydanticAI multi-agent system
- [x] Kai main agent
- [x] Guardrail agent
- [x] Genetic counseling agent
- [x] Mental wellness agent
- [x] Agent orchestration system

**In Progress:**
- [ ] Database integration (PostgreSQL)
- [ ] User authentication system
- [ ] Journaling module
- [ ] Document/image upload
- [ ] Encryption layer
- [ ] Frontend chat interface
- [ ] Frontend auth pages
- [ ] Testing suite
- [x] Docker deployment configuration
- [ ] Mobile app foundation

### 🔮 Future Phases

**Phase 2 - Proactive Intelligence**
- Trait mapping + user profiles
- Proactive remediation logic
- Notification framework
- AI insight summaries
- Human coach flag system

**Phase 3 - Engagement Layer**
- Gamification system
- Reflective prompts
- Personalized journaling themes
- Adaptive AI tone
- Curated experience engine

**Phase 4 - Expansion & Monetization**
- Social network integration
- Deployment automation
- Advanced notifications
- Subscription model
- Partner API endpoints

**Phase 5 - Ethical & Evolutionary Systems**
- Materialism → Altruism metrics
- Transparency dashboards
- AI self-correction
- Anonymized insight network
- Open research layer

## 🧪 Testing

### Test the API
```bash
# Health check
curl http://localhost:8000/health

# Chat with Kai
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "Hello, I'm feeling anxious today"
  }'
```

## 📊 Project Management

This project is managed through Archon project boards:
- **View Boards**: http://localhost:3737
- **Phase 1 Board**: Track current development progress
- **Phases 2-5 Boards**: Future roadmap planning

## 🤝 Contributing

This is currently a personal development project. Phase 1 is under active development.

## ⚠️ Important Notes

**Not a Replacement for Therapy**
- Kai is a supportive companion, not a licensed therapist
- Always seek professional help for serious mental health concerns
- Crisis resources are provided when appropriate

**Privacy & Data**
- End-to-end encryption planned for Phase 1
- User data control and transparency are core principles
- HIPAA compliance considerations for future versions

## 📝 License

TBD

## 💙 Mission Statement

"Be the person you needed" - Kai exists to provide the support, empathy, and understanding that everyone deserves on their wellness journey.

---

**Project Status**: Phase 1 - Core Infrastructure (In Development)
**Tech Stack**: Next.js + FastAPI + PydanticAI
**AI System**: Multi-agent architecture with OpenAI-compatible LLMs
**Started**: October 2025
