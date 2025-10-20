"""Pydantic models for agent communication."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Agent role identifiers."""

    KAI = "kai"
    GUARDRAIL = "guardrail"
    GENETIC = "genetic"
    WELLNESS = "wellness"


class MessageSafety(str, Enum):
    """Safety assessment levels."""

    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


class UserTrait(BaseModel):
    """User personality/behavioral trait."""

    name: str
    value: float = Field(ge=0.0, le=1.0, description="Trait strength (0-1)")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in assessment (0-1)")


class UserProfile(BaseModel):
    """User genetic profile for AI personalization."""

    user_id: str
    traits: list[UserTrait] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    communication_style: str = "supportive"


class GuardrailResult(BaseModel):
    """Result from guardrail agent assessment."""

    safety: MessageSafety
    reason: str | None = None
    suggested_response: str | None = None


class WellnessInsight(BaseModel):
    """Mental wellness insight from analysis."""

    category: str
    insight: str
    severity: str = Field(description="low, medium, high")
    recommendations: list[str] = Field(default_factory=list)


class AgentMessage(BaseModel):
    """Message passed between agents."""

    role: AgentRole
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Response from an agent."""

    agent_role: AgentRole
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
