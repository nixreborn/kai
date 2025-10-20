# Journal Module Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Journal List │  │ Create Entry │  │ Entry Detail │          │
│  │   page.tsx   │  │  new/page    │  │  [id]/page   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│          │                 │                  │                  │
│          └─────────────────┴──────────────────┘                  │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Python)                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Journal API Router                           │  │
│  │         /api/journal/* (8 endpoints)                      │  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │    CRUD      │  │  AI Analysis │  │   Insights   │   │  │
│  │  │  Endpoints   │  │  Endpoints   │  │  Endpoints   │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│             │                    │                               │
│             │                    └───────────────┐               │
│             ▼                                    ▼               │
│  ┌────────────────────┐              ┌────────────────────┐    │
│  │  Database Layer    │              │   AI Agent Layer   │    │
│  │  (SQLAlchemy)      │              │   (PydanticAI)     │    │
│  │                    │              │                    │    │
│  │  ┌──────────────┐  │              │  ┌──────────────┐ │    │
│  │  │ JournalEntry │  │              │  │ Wellness     │ │    │
│  │  │    Model     │  │              │  │   Agent      │ │    │
│  │  └──────────────┘  │              │  └──────────────┘ │    │
│  │  ┌──────────────┐  │              │  ┌──────────────┐ │    │
│  │  │   User       │  │              │  │  Kai Agent   │ │    │
│  │  │   Model      │  │              │  │  (Prompts)   │ │    │
│  │  └──────────────┘  │              │  └──────────────┘ │    │
│  └────────────────────┘              └────────────────────┘    │
│             │                                    │               │
└─────────────┼────────────────────────────────────┼───────────────┘
              ▼                                    ▼
┌─────────────────────────┐          ┌─────────────────────────┐
│   PostgreSQL Database   │          │   Local LLM Server      │
│                         │          │  (OpenAI-compatible)    │
│  ┌──────────────────┐   │          │                         │
│  │ journal_entries  │   │          │  ┌──────────────────┐   │
│  │                  │   │          │  │  Analysis Model  │   │
│  │  - id (UUID)     │   │          │  │  (Wellness)      │   │
│  │  - user_id       │   │          │  └──────────────────┘   │
│  │  - content       │   │          │  ┌──────────────────┐   │
│  │  - mood          │   │          │  │  Prompt Model    │   │
│  │  - tags          │   │          │  │  (Kai)           │   │
│  │  - ai_insights   │   │          │  └──────────────────┘   │
│  └──────────────────┘   │          └─────────────────────────┘
└─────────────────────────┘
```

## Data Flow

### 1. Create Journal Entry Flow

```
User Input (Frontend)
    │
    ├─> JournalEntryCreate (Pydantic validation)
    │
    ├─> POST /api/journal/entries?user_id=xxx
    │
    ├─> journal.create_journal_entry()
    │   │
    │   ├─> Create JournalEntry database model
    │   │
    │   ├─> db.add() → db.commit()
    │   │
    │   └─> Return JournalEntryResponse
    │
    └─> Display in UI with success message
```

### 2. AI Analysis Flow

```
User clicks "Analyze"
    │
    ├─> POST /api/journal/entries/{id}/analyze?user_id=xxx
    │
    ├─> journal.analyze_journal_entry()
    │   │
    │   ├─> Fetch entry from database
    │   │
    │   ├─> Format entry text
    │   │
    │   ├─> Call wellness_agent.analyze_wellness_patterns()
    │   │   │
    │   │   ├─> Send to Local LLM
    │   │   │
    │   │   └─> Receive WellnessInsight objects
    │   │
    │   ├─> Convert to JournalInsight format
    │   │
    │   ├─> Determine sentiment
    │   │
    │   ├─> Extract themes
    │   │
    │   ├─> Store results in entry.ai_insights
    │   │
    │   └─> Return JournalAnalysisResponse
    │
    └─> Display insights in UI
```

### 3. Generate Prompts Flow

```
User opens journal
    │
    ├─> GET /api/journal/prompts?user_id=xxx
    │
    ├─> journal.get_journal_prompts()
    │   │
    │   ├─> Call prompt_agent.run()
    │   │   │
    │   │   ├─> Send prompt generation request to LLM
    │   │   │
    │   │   └─> Receive list of JournalPrompt objects
    │   │
    │   └─> Return JournalPromptsResponse
    │
    └─> Display prompts in sidebar/card
```

### 4. Wellness Insights Flow

```
User views dashboard
    │
    ├─> GET /api/journal/insights?user_id=xxx&days=30
    │
    ├─> journal.get_journal_insights()
    │   │
    │   ├─> Query recent entries from database
    │   │
    │   ├─> Calculate mood trend (recent vs older)
    │   │
    │   ├─> Calculate writing streak
    │   │
    │   ├─> Format entries for analysis
    │   │
    │   ├─> Call wellness_agent.analyze_wellness_patterns()
    │   │   │
    │   │   ├─> Send journal history to LLM
    │   │   │
    │   │   └─> Receive pattern insights
    │   │
    │   └─> Return JournalInsightsResponse
    │
    └─> Display trends, streaks, and insights
```

## Component Hierarchy

### Backend

```
src/
├── api/
│   └── journal.py              # 8 API endpoints
├── models/
│   ├── database.py             # SQLAlchemy models
│   ├── journal_models.py       # Pydantic schemas
│   └── agent_models.py         # AI agent models
├── core/
│   ├── config.py               # Settings
│   ├── database.py             # DB session management
│   └── llm_client.py           # LLM client setup
└── agents/
    ├── wellness_agent.py       # Mental health analysis
    └── kai_agent.py            # Conversational prompts
```

### Frontend (To be implemented)

```
app/journal/
├── page.tsx                    # Main journal list view
├── new/
│   └── page.tsx                # Create new entry
├── [id]/
│   └── page.tsx                # View/edit entry
└── components/
    ├── JournalEntry.tsx        # Entry card component
    ├── JournalList.tsx         # List with filters
    ├── MoodSelector.tsx        # Mood input widget
    ├── TagInput.tsx            # Tag management
    ├── JournalPrompts.tsx      # AI prompts display
    └── InsightsPanel.tsx       # Wellness dashboard
```

## Security Layers

```
┌────────────────────────────────────────────────────────┐
│ Layer 1: Frontend Authentication                       │
│ - User login via auth module                           │
│ - JWT token in requests                                │
└────────────────────────────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────────────┐
│ Layer 2: API Parameter Validation                      │
│ - Require user_id query parameter                      │
│ - Validate with Pydantic models                        │
└────────────────────────────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────────────┐
│ Layer 3: User-Scoped Database Queries                  │
│ - All queries filter by user_id                        │
│ - No cross-user data access                            │
└────────────────────────────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────────────┐
│ Layer 4: Database-Level Security                       │
│ - PostgreSQL user permissions                          │
│ - Encrypted connections                                │
│ - Data at rest encryption                              │
└────────────────────────────────────────────────────────┘
```

## AI Agent Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Journal Module                         │
└──────────────────────────────────────────────────────────┘
                    │
                    ├───────────────┬──────────────────┐
                    ▼               ▼                  ▼
        ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
        │ Wellness Agent  │ │  Kai Agent  │ │  Guardrail      │
        │   (Analysis)    │ │  (Prompts)  │ │  Agent          │
        └─────────────────┘ └─────────────┘ └─────────────────┘
                    │               │                  │
                    └───────────────┴──────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │   LLM Client          │
                        │   (OpenAI-compatible) │
                        └───────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  Local LLM Server     │
                        │  (vLLM/Ollama/etc)    │
                        └───────────────────────┘
```

### Agent Responsibilities

1. **Wellness Agent**
   - Analyzes journal entries for mental health patterns
   - Identifies mood, behavioral, cognitive, emotional, social patterns
   - Assigns severity levels (low/medium/high)
   - Provides compassionate recommendations
   - Used in: Entry analysis, Historical insights

2. **Kai Agent**
   - Generates personalized journal prompts
   - Uses trauma-informed language
   - Incorporates water/aqua metaphors
   - Provides diverse prompt categories
   - Used in: Prompt generation

3. **Guardrail Agent** (from orchestrator)
   - Monitors for crisis situations
   - Blocks harmful content
   - Escalates to professional help when needed
   - Used in: Content safety checks

## Database Schema Details

### journal_entries Table

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID | Primary key | NOT NULL, DEFAULT uuid_generate_v4() |
| user_id | VARCHAR(255) | User identifier | NOT NULL, INDEXED |
| title | VARCHAR(500) | Optional entry title | NULL |
| content | TEXT | Journal entry text | NOT NULL |
| mood | FLOAT | Mood rating 1-10 | NULL, CHECK >= 1 AND <= 10 |
| mood_emoji | VARCHAR(10) | Mood emoji | NULL |
| tags | JSON | Array of tag strings | DEFAULT '[]' |
| images | JSON | Array of image URLs | DEFAULT '[]' |
| ai_insights | JSON | Cached AI analysis | NULL |
| created_at | TIMESTAMP | Creation time | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update time | NOT NULL, DEFAULT NOW() |

### Indexes

- PRIMARY KEY on id
- INDEX on user_id (for user-scoped queries)
- INDEX on created_at (for date-based queries)
- GIN INDEX on tags (for efficient tag filtering - PostgreSQL specific)

## API Response Times (Estimated)

| Endpoint | Avg Response Time | Notes |
|----------|-------------------|-------|
| POST /entries | 50-100ms | Database insert |
| GET /entries | 100-200ms | Paginated list with filters |
| GET /entries/{id} | 20-50ms | Single record fetch |
| PUT /entries/{id} | 50-100ms | Database update |
| DELETE /entries/{id} | 30-60ms | Database delete |
| POST /entries/{id}/analyze | 2-5s | LLM processing time |
| GET /prompts | 2-4s | LLM generation time |
| GET /insights | 3-6s | Multiple entries + LLM analysis |

Note: AI endpoints are slower due to LLM processing. Consider:
- Caching analyzed entries (already implemented)
- Background job processing for insights
- Loading indicators in UI

## Scalability Considerations

### Database
- Connection pooling (5 connections, 10 max overflow)
- Async queries for non-blocking I/O
- Indexed fields for fast queries
- JSON columns for flexible data (tags, images, insights)

### AI Processing
- On-demand analysis (user-initiated)
- Results caching in database
- Can be moved to background jobs if needed
- LLM server can be scaled independently

### API
- Async FastAPI for high concurrency
- Pagination for large datasets
- User-scoped queries reduce data volume
- CORS configured for multiple frontends

## Monitoring & Observability

### Recommended Metrics

1. **API Metrics**
   - Request count by endpoint
   - Response times (p50, p95, p99)
   - Error rates
   - User activity patterns

2. **Database Metrics**
   - Query performance
   - Connection pool usage
   - Table sizes
   - Index usage

3. **AI Metrics**
   - LLM response times
   - Analysis success rate
   - Prompt quality feedback
   - Cache hit rate

4. **User Metrics**
   - Daily active journalers
   - Average entries per user
   - Writing streak distribution
   - Feature usage (analysis, prompts, insights)

## Error Handling

```python
try:
    # Process request
    result = await process_journal_entry()
    return result
except ValueError as e:
    # Validation error
    raise HTTPException(status_code=422, detail=str(e))
except NotFoundError:
    # Resource not found
    raise HTTPException(status_code=404, detail="Entry not found")
except PermissionError:
    # User doesn't own resource
    raise HTTPException(status_code=403, detail="Access denied")
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Future Enhancements

1. **Scheduled Insights**
   - Background job to generate weekly insights
   - Email/push notifications for patterns
   - Proactive check-ins based on mood trends

2. **Rich Media Support**
   - Voice notes transcription
   - Image upload and storage
   - Drawing/sketch support

3. **Advanced Analytics**
   - Correlation analysis (mood vs tags, activities)
   - Predictive mood forecasting
   - Trigger identification

4. **Social Features**
   - Share anonymized insights with therapist
   - Community challenges (writing streaks)
   - Support group integration

5. **Export & Backup**
   - PDF export of entries
   - JSON backup download
   - Import from other journal apps
