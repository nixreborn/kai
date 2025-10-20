"""Pydantic models for journal endpoints."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class JournalEntryCreate(BaseModel):
    """Request model for creating a journal entry."""

    title: str | None = Field(None, description="Optional entry title", max_length=500)
    content: str = Field(..., description="Journal entry content", min_length=1)
    mood: float | None = Field(None, ge=1.0, le=10.0, description="Mood rating (1-10)")
    mood_emoji: str | None = Field(None, description="Mood emoji", max_length=10)
    tags: list[str] = Field(default_factory=list, description="Entry tags")
    images: list[str] = Field(default_factory=list, description="Image URLs/paths")


class JournalEntryUpdate(BaseModel):
    """Request model for updating a journal entry."""

    title: str | None = Field(None, description="Optional entry title", max_length=500)
    content: str | None = Field(None, description="Journal entry content", min_length=1)
    mood: float | None = Field(None, ge=1.0, le=10.0, description="Mood rating (1-10)")
    mood_emoji: str | None = Field(None, description="Mood emoji", max_length=10)
    tags: list[str] | None = Field(None, description="Entry tags")
    images: list[str] | None = Field(None, description="Image URLs/paths")


class JournalEntryResponse(BaseModel):
    """Response model for a journal entry."""

    id: UUID
    user_id: str
    title: str | None
    content: str
    mood: float | None
    mood_emoji: str | None
    tags: list[str]
    images: list[str]
    ai_insights: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JournalEntryList(BaseModel):
    """Response model for list of journal entries."""

    entries: list[JournalEntryResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class JournalPrompt(BaseModel):
    """AI-generated journal prompt."""

    prompt: str = Field(description="Journaling prompt text")
    category: str = Field(description="Prompt category (reflection, gratitude, emotions, etc.)")


class JournalPromptsResponse(BaseModel):
    """Response with multiple journal prompts."""

    prompts: list[JournalPrompt]


class JournalInsight(BaseModel):
    """Wellness insight from journal analysis."""

    category: str = Field(description="Insight category (mood, patterns, growth, etc.)")
    insight: str = Field(description="The insight text")
    severity: str = Field(description="Severity level: low, medium, high")
    recommendations: list[str] = Field(description="Actionable recommendations")
    time_period: str = Field(description="Time period analyzed (e.g., 'last 7 days')")


class JournalInsightsResponse(BaseModel):
    """Response with wellness insights from journal history."""

    insights: list[JournalInsight]
    entries_analyzed: int
    time_period: str
    mood_trend: str | None = Field(None, description="Overall mood trend (improving, stable, declining)")
    writing_streak: int = Field(0, description="Current consecutive days of journaling")


class JournalAnalysisResponse(BaseModel):
    """Response from AI analysis of a specific entry."""

    insights: list[JournalInsight]
    sentiment: str = Field(description="Overall sentiment (positive, neutral, negative, mixed)")
    themes: list[str] = Field(description="Main themes identified in entry")
    suggestions: list[str] = Field(description="Gentle suggestions or reflections")
