# Journal Module Quick Start Guide

## API Endpoints at a Glance

All endpoints require `user_id` query parameter for user-scoped access.

### Basic CRUD

```bash
# Create entry
POST /api/journal/entries?user_id=user123
Body: { "content": "...", "mood": 7.5, "tags": [...] }

# List entries (with filters)
GET /api/journal/entries?user_id=user123&page=1&search=peaceful&tags=gratitude&mood_min=6

# Get specific entry
GET /api/journal/entries/{entry_id}?user_id=user123

# Update entry
PUT /api/journal/entries/{entry_id}?user_id=user123
Body: { "content": "updated...", "mood": 8.0 }

# Delete entry
DELETE /api/journal/entries/{entry_id}?user_id=user123
```

### AI-Powered Features

```bash
# Get AI-generated prompts
GET /api/journal/prompts?user_id=user123

# Analyze specific entry
POST /api/journal/entries/{entry_id}/analyze?user_id=user123

# Get wellness insights from history
GET /api/journal/insights?user_id=user123&days=30
```

## Quick Test Commands

```bash
# Test with curl
curl -X POST "http://localhost:8000/api/journal/entries?user_id=test123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Entry",
    "content": "Today was a good day. I felt peaceful.",
    "mood": 7.5,
    "mood_emoji": "😊",
    "tags": ["peaceful", "gratitude"]
  }'

# Get prompts
curl "http://localhost:8000/api/journal/prompts?user_id=test123"

# List entries
curl "http://localhost:8000/api/journal/entries?user_id=test123&page=1"
```

## Data Models

### Create Entry
```json
{
  "title": "Optional Title",
  "content": "Required entry text",
  "mood": 7.5,  // 1-10, optional
  "mood_emoji": "😊",  // optional
  "tags": ["tag1", "tag2"],  // optional
  "images": []  // optional
}
```

### Entry Response
```json
{
  "id": "uuid",
  "user_id": "user123",
  "title": "...",
  "content": "...",
  "mood": 7.5,
  "mood_emoji": "😊",
  "tags": [...],
  "images": [],
  "ai_insights": { ... },
  "created_at": "2025-10-20T12:00:00Z",
  "updated_at": "2025-10-20T12:00:00Z"
}
```

## Integration with Kai Agents

### Wellness Agent
- Analyzes journal entries for mental health patterns
- Identifies mood, behavioral, cognitive, emotional, social patterns
- Provides severity-based recommendations (low/medium/high)

### Kai Agent
- Generates personalized journal prompts
- Uses trauma-informed, supportive language
- Incorporates water/aqua metaphors

## Common Use Cases

### Daily Journaling Flow
1. User opens app → Show prompts from `/api/journal/prompts`
2. User writes → Auto-save to localStorage
3. User submits → POST to `/api/journal/entries`
4. Optional: Analyze entry → POST to `/api/journal/entries/{id}/analyze`

### Dashboard Display
1. Fetch recent entries → GET `/api/journal/entries?page=1&page_size=5`
2. Show writing streak → GET `/api/journal/insights?days=7`
3. Display mood chart → Parse mood from recent entries

### Search & Filter
```
GET /api/journal/entries?user_id=user123
  &search=peaceful           # Search in title/content
  &tags=gratitude,nature     # Filter by tags
  &mood_min=6&mood_max=9     # Mood range
  &start_date=2025-10-01     # Date range
  &page=1&page_size=20       # Pagination
```

## Files to Know

- **API**: `/home/nix/projects/kai/backend/src/api/journal.py`
- **Models**: `/home/nix/projects/kai/backend/src/models/journal_models.py`
- **Database**: `/home/nix/projects/kai/backend/src/models/database.py`
- **Docs**: `/home/nix/projects/kai/backend/JOURNAL_API.md`

## Running the Server

```bash
# Activate venv
cd /home/nix/projects/kai/backend
source .venv/bin/activate

# Start server
uvicorn src.main:app --reload --port 8000

# View API docs
open http://localhost:8000/docs
```

## Environment Variables

Required in `.env`:
```
DATABASE_URL=postgresql+asyncpg://kai:kai@localhost:5432/kai_db
LLM_BASE_URL=http://192.168.1.7:8000/v1
LLM_API_KEY=optional-api-key
LLM_MODEL=default
```

## Frontend Components Needed

Create in `/home/nix/projects/kai/frontend/app/journal/`:

1. **page.tsx** - Main journal list view
2. **new/page.tsx** - Create new entry
3. **[id]/page.tsx** - View/edit entry
4. **components/JournalEntry.tsx** - Entry card
5. **components/JournalList.tsx** - List with filters
6. **components/MoodSelector.tsx** - Mood input
7. **components/TagInput.tsx** - Tag management
8. **components/JournalPrompts.tsx** - AI prompts display
9. **components/InsightsPanel.tsx** - Wellness insights

## Key Features

✅ Full CRUD operations
✅ AI-powered analysis
✅ Personalized prompts
✅ Mood tracking & trends
✅ Writing streak tracking
✅ Advanced search & filters
✅ Privacy-first (user-scoped)
✅ Auto-save support ready
✅ Mobile-friendly API design

## Support

See full documentation:
- API Reference: `JOURNAL_API.md`
- Implementation Details: `JOURNAL_IMPLEMENTATION.md`
- OpenAPI/Swagger Docs: http://localhost:8000/docs
