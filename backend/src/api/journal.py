"""Journal endpoints for the Kai mental wellness platform."""

from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic_ai import Agent
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.wellness_agent import analyze_wellness_patterns
from ..auth.dependencies import get_current_active_user
from ..core.database import get_db
from ..core.llm_client import get_llm_model
from ..models.database import JournalEntry, User
from ..models.journal_models import (
    JournalAnalysisResponse,
    JournalEntryCreate,
    JournalEntryList,
    JournalEntryResponse,
    JournalEntryUpdate,
    JournalInsight,
    JournalInsightsResponse,
    JournalPrompt,
    JournalPromptsResponse,
)
from ..security.dependencies import get_encryption_service
from ..security.encryption import EncryptionService
from ..security.journal_encryption import (
    decrypt_journal_entry_in_place,
    encrypt_journal_entry,
)

router = APIRouter(prefix="/api/journal", tags=["journal"])

# AI agent for generating journal prompts
PROMPT_SYSTEM = """You are Kai, helping users with thoughtful journal prompts.

Generate 3-5 diverse journal prompts that:
- Encourage self-reflection and emotional awareness
- Are open-ended and non-judgmental
- Cover different categories: gratitude, emotions, relationships, growth, challenges
- Use gentle, supportive language
- Incorporate water/flow metaphors occasionally
- Are specific enough to guide but open enough to explore

Return as JSON array with format:
[
  {"prompt": "What emotion has been flowing through you most today?", "category": "emotions"},
  {"prompt": "What are you grateful for in this moment?", "category": "gratitude"}
]"""

prompt_agent = Agent(
    model=get_llm_model(),
    system_prompt=PROMPT_SYSTEM,
    output_type=list[JournalPrompt],
)


@router.post("/entries", response_model=JournalEntryResponse, status_code=201)
async def create_journal_entry(
    entry: JournalEntryCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    encryption_service: Annotated[EncryptionService | None, Depends(get_encryption_service)] = None,
) -> JournalEntry:
    """
    Create a new journal entry.

    This endpoint allows users to save their journal entries with optional mood tracking,
    tags, and images. If the user has encryption configured and provides the encryption
    password in the X-Encryption-Password header, the entry will be encrypted.
    """
    # Create new journal entry
    db_entry = JournalEntry(
        user_id=current_user.id,
        content=entry.content,
        tags=entry.tags,
        mood=entry.mood,
    )

    # Encrypt if encryption service is available
    if encryption_service:
        await encrypt_journal_entry(db_entry, encryption_service)

    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)

    # Decrypt for response if encrypted
    if encryption_service and db_entry.is_encrypted:
        await decrypt_journal_entry_in_place(db_entry, encryption_service)

    return db_entry


@router.get("/entries", response_model=JournalEntryList)
async def list_journal_entries(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    encryption_service: Annotated[EncryptionService | None, Depends(get_encryption_service)] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search in title and content"),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    mood_min: float | None = Query(None, ge=1.0, le=10.0, description="Minimum mood rating"),
    mood_max: float | None = Query(None, ge=1.0, le=10.0, description="Maximum mood rating"),
    start_date: datetime | None = Query(None, description="Filter entries from this date"),
    end_date: datetime | None = Query(None, description="Filter entries until this date"),
) -> JournalEntryList:
    """
    List user's journal entries with pagination, search, and filters.

    Supports:
    - Full-text search in title and content
    - Tag filtering
    - Mood range filtering
    - Date range filtering
    """
    # Build query
    query = select(JournalEntry).where(JournalEntry.user_id == current_user.id)

    # Apply filters
    if search:
        search_filter = or_(
            JournalEntry.title.ilike(f"%{search}%"),
            JournalEntry.content.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    if tags:
        # Filter entries that contain any of the specified tags
        # Note: This is a simple implementation. For better performance with large datasets,
        # consider using PostgreSQL's array operators or a separate tags table
        for tag in tags:
            query = query.where(JournalEntry.tags.contains([tag]))

    if mood_min is not None:
        query = query.where(JournalEntry.mood >= mood_min)

    if mood_max is not None:
        query = query.where(JournalEntry.mood <= mood_max)

    if start_date:
        query = query.where(JournalEntry.created_at >= start_date)

    if end_date:
        query = query.where(JournalEntry.created_at <= end_date)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(desc(JournalEntry.created_at))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    entries = list(result.scalars().all())

    # Decrypt entries if encryption service is available
    if encryption_service:
        for entry in entries:
            if entry.is_encrypted:
                await decrypt_journal_entry_in_place(entry, encryption_service)

    return JournalEntryList(
        entries=entries,
        total=total,
        page=page,
        page_size=page_size,
        has_more=total > (page * page_size),
    )


@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    encryption_service: Annotated[EncryptionService | None, Depends(get_encryption_service)] = None,
) -> JournalEntry:
    """Get a specific journal entry by ID."""
    query = select(JournalEntry).where(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id,
    )
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    # Decrypt if encrypted and service available
    if encryption_service and entry.is_encrypted:
        await decrypt_journal_entry_in_place(entry, encryption_service)

    return entry


@router.put("/entries/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: UUID,
    entry_update: JournalEntryUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    encryption_service: Annotated[EncryptionService | None, Depends(get_encryption_service)] = None,
) -> JournalEntry:
    """Update a journal entry."""
    # Get existing entry
    query = select(JournalEntry).where(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id,
    )
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    # Update fields
    update_data = entry_update.model_dump(exclude_unset=True)

    # If content is being updated and entry is encrypted, re-encrypt
    if "content" in update_data and encryption_service and entry.is_encrypted:
        entry.content = update_data["content"]
        await encrypt_journal_entry(entry, encryption_service)
        # Remove content from update_data as it's already handled
        update_data.pop("content")

    # Update remaining fields
    for field, value in update_data.items():
        setattr(entry, field, value)

    await db.commit()
    await db.refresh(entry)

    # Decrypt for response if encrypted
    if encryption_service and entry.is_encrypted:
        await decrypt_journal_entry_in_place(entry, encryption_service)

    return entry


@router.delete("/entries/{entry_id}", status_code=204)
async def delete_journal_entry(
    entry_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a journal entry."""
    query = select(JournalEntry).where(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id,
    )
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    await db.delete(entry)
    await db.commit()


@router.post("/entries/{entry_id}/analyze", response_model=JournalAnalysisResponse)
async def analyze_journal_entry(
    entry_id: UUID,
    user_id: str = Query(..., description="User identifier"),
    db: AsyncSession = Depends(get_db),
) -> JournalAnalysisResponse:
    """
    Get AI analysis of a specific journal entry.

    Uses the wellness agent to provide:
    - Emotional insights
    - Identified themes
    - Gentle suggestions and reflections
    """
    # Get the journal entry
    query = select(JournalEntry).where(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == user_id,
    )
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    # Analyze with wellness agent
    insights = await analyze_wellness_patterns(
        conversation_history="",
        journal_entries=f"Title: {entry.title or 'Untitled'}\nDate: {entry.created_at}\nMood: {entry.mood or 'Not specified'}\nContent: {entry.content}",
    )

    # Convert wellness insights to journal insights
    journal_insights = [
        JournalInsight(
            category=insight.category,
            insight=insight.insight,
            severity=insight.severity,
            recommendations=insight.recommendations,
            time_period="This entry",
        )
        for insight in insights
    ]

    # Determine overall sentiment
    severity_levels = [i.severity for i in insights]
    if "high" in severity_levels:
        sentiment = "negative"
    elif "medium" in severity_levels:
        sentiment = "mixed"
    else:
        sentiment = "positive" if insights else "neutral"

    # Extract themes from insights
    themes = list({insight.category for insight in insights})

    # Create suggestions from recommendations
    all_recommendations = []
    for insight in insights:
        all_recommendations.extend(insight.recommendations[:2])  # Take top 2 from each

    # Store AI insights in the entry for future reference
    entry.ai_insights = {
        "analyzed_at": datetime.utcnow().isoformat(),
        "sentiment": sentiment,
        "themes": themes,
        "insights": [
            {
                "category": i.category,
                "insight": i.insight,
                "severity": i.severity,
            }
            for i in insights
        ],
    }
    await db.commit()

    return JournalAnalysisResponse(
        insights=journal_insights,
        sentiment=sentiment,
        themes=themes,
        suggestions=all_recommendations[:5],  # Return top 5 suggestions
    )


@router.get("/prompts", response_model=JournalPromptsResponse)
async def get_journal_prompts(
    user_id: str = Query(..., description="User identifier"),
) -> JournalPromptsResponse:
    """
    Get AI-generated journal prompts to inspire writing.

    Uses Kai agent to generate personalized, thoughtful prompts.
    """
    # Generate prompts using the prompt agent
    result = await prompt_agent.run("Generate diverse journal prompts for today")

    return JournalPromptsResponse(prompts=result.data)


@router.get("/insights", response_model=JournalInsightsResponse)
async def get_journal_insights(
    user_id: str = Query(..., description="User identifier"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
) -> JournalInsightsResponse:
    """
    Get wellness insights from journal history.

    Analyzes recent journal entries to identify:
    - Mood patterns and trends
    - Behavioral patterns
    - Writing habits and streaks
    - Personalized recommendations
    """
    # Get recent entries
    start_date = datetime.utcnow() - timedelta(days=days)
    query = (
        select(JournalEntry)
        .where(
            JournalEntry.user_id == user_id,
            JournalEntry.created_at >= start_date,
        )
        .order_by(desc(JournalEntry.created_at))
    )

    result = await db.execute(query)
    entries = list(result.scalars().all())

    if not entries:
        return JournalInsightsResponse(
            insights=[],
            entries_analyzed=0,
            time_period=f"last {days} days",
            mood_trend=None,
            writing_streak=0,
        )

    # Calculate mood trend
    mood_entries = [e for e in entries if e.mood is not None]
    mood_trend = None
    if len(mood_entries) >= 2:
        recent_moods = [e.mood for e in mood_entries[:len(mood_entries) // 2]]
        older_moods = [e.mood for e in mood_entries[len(mood_entries) // 2:]]

        if recent_moods and older_moods:
            recent_avg = sum(recent_moods) / len(recent_moods)
            older_avg = sum(older_moods) / len(older_moods)

            if recent_avg > older_avg + 0.5:
                mood_trend = "improving"
            elif recent_avg < older_avg - 0.5:
                mood_trend = "declining"
            else:
                mood_trend = "stable"

    # Calculate writing streak
    writing_streak = 0
    current_date = datetime.utcnow().date()
    entry_dates = sorted({e.created_at.date() for e in entries}, reverse=True)

    for entry_date in entry_dates:
        if entry_date == current_date - timedelta(days=writing_streak):
            writing_streak += 1
        else:
            break

    # Prepare journal text for analysis
    journal_text = "\n\n---\n\n".join(
        [
            f"Date: {e.created_at.strftime('%Y-%m-%d')}\n"
            f"Title: {e.title or 'Untitled'}\n"
            f"Mood: {e.mood or 'Not specified'}\n"
            f"Tags: {', '.join(e.tags) if e.tags else 'None'}\n"
            f"Content: {e.content[:500]}{'...' if len(e.content) > 500 else ''}"
            for e in entries[:10]  # Analyze most recent 10 entries
        ]
    )

    # Analyze with wellness agent
    wellness_insights = await analyze_wellness_patterns(
        conversation_history="",
        journal_entries=journal_text,
    )

    # Convert to journal insights with time period
    journal_insights = [
        JournalInsight(
            category=insight.category,
            insight=insight.insight,
            severity=insight.severity,
            recommendations=insight.recommendations,
            time_period=f"last {days} days",
        )
        for insight in wellness_insights
    ]

    return JournalInsightsResponse(
        insights=journal_insights,
        entries_analyzed=len(entries),
        time_period=f"last {days} days",
        mood_trend=mood_trend,
        writing_streak=writing_streak,
    )
