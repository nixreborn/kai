"""Test configuration and fixtures."""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Any

from src.models.agent_models import (
    UserProfile,
    UserTrait,
    GuardrailResult,
    MessageSafety,
    WellnessInsight,
    AgentResponse,
    AgentRole,
)


@pytest.fixture
def mock_user_profile() -> UserProfile:
    """Create a mock user profile for testing."""
    return UserProfile(
        user_id="test_user_123",
        traits=[
            UserTrait(name="emotional_expression", value=0.7, confidence=0.8),
            UserTrait(name="support_needs", value=0.6, confidence=0.7),
        ],
        preferences={"theme": "aqua"},
        communication_style="supportive",
    )


@pytest.fixture
def empty_user_profile() -> UserProfile:
    """Create an empty user profile for testing."""
    return UserProfile(
        user_id="new_user_456",
        traits=[],
        preferences={},
        communication_style="supportive",
    )


@pytest.fixture
def safe_guardrail_result() -> GuardrailResult:
    """Create a safe guardrail result."""
    return GuardrailResult(
        safety=MessageSafety.SAFE,
        reason=None,
        suggested_response=None,
    )


@pytest.fixture
def warning_guardrail_result() -> GuardrailResult:
    """Create a warning guardrail result."""
    return GuardrailResult(
        safety=MessageSafety.WARNING,
        reason="User mentions feeling stressed and overwhelmed",
        suggested_response=None,
    )


@pytest.fixture
def blocked_guardrail_result() -> GuardrailResult:
    """Create a blocked guardrail result."""
    return GuardrailResult(
        safety=MessageSafety.BLOCKED,
        reason="User expresses suicidal ideation requiring immediate intervention",
        suggested_response="I'm very concerned about what you've shared. Please reach out to a crisis helpline immediately: National Suicide Prevention Lifeline at 988.",
    )


@pytest.fixture
def wellness_insights() -> list[WellnessInsight]:
    """Create sample wellness insights."""
    return [
        WellnessInsight(
            category="mood",
            insight="User shows signs of low mood and reduced energy over past conversations",
            severity="medium",
            recommendations=[
                "Encourage gentle physical activity",
                "Suggest checking in with support network",
                "Monitor for changes in sleep patterns",
            ],
        ),
        WellnessInsight(
            category="cognitive",
            insight="Pattern of catastrophizing and negative self-talk observed",
            severity="medium",
            recommendations=[
                "Practice cognitive reframing exercises",
                "Encourage mindfulness and present-moment awareness",
            ],
        ),
    ]


@pytest.fixture
def high_severity_wellness_insight() -> WellnessInsight:
    """Create a high severity wellness insight."""
    return WellnessInsight(
        category="mood",
        insight="Persistent depressive symptoms and loss of interest in activities",
        severity="high",
        recommendations=[
            "Strongly recommend professional mental health evaluation",
            "Discuss safety planning and support resources",
            "Monitor for crisis indicators",
        ],
    )


@pytest.fixture
def user_traits() -> list[UserTrait]:
    """Create sample user traits."""
    return [
        UserTrait(name="communication_style_direct", value=0.3, confidence=0.7),
        UserTrait(name="communication_style_gentle", value=0.8, confidence=0.8),
        UserTrait(name="reflection_depth", value=0.7, confidence=0.6),
        UserTrait(name="emotional_openness", value=0.9, confidence=0.8),
    ]


@pytest.fixture
def conversation_history() -> list[dict[str, str]]:
    """Create sample conversation history."""
    return [
        {"role": "user", "content": "I've been feeling really stressed lately"},
        {"role": "assistant", "content": "I hear that you're feeling stressed. Can you tell me more about what's been weighing on you?"},
        {"role": "user", "content": "Work has been overwhelming and I can't seem to catch up"},
        {"role": "assistant", "content": "That sounds really challenging. Like waves that keep coming, it can feel endless. Have you been able to take any time for yourself?"},
        {"role": "user", "content": "Not really, I feel guilty when I try to rest"},
        {"role": "assistant", "content": "It's understandable to feel that way, but rest is essential. Your well-being matters."},
    ]


@pytest.fixture
def mock_llm_response() -> Mock:
    """Create a mock LLM response."""
    mock = Mock()
    mock.data = "I'm here for you. It sounds like you're going through a difficult time."
    return mock


@pytest.fixture
def mock_llm_agent(mock_llm_response: Mock) -> AsyncMock:
    """Create a mock LLM agent."""
    agent = AsyncMock()
    agent.run = AsyncMock(return_value=mock_llm_response)
    return agent


class MockLLMModel:
    """Mock LLM model for testing without actual API calls."""

    def __init__(self, response_data: Any = None):
        """Initialize mock model."""
        self.response_data = response_data or "Mock response"

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Mock call method."""
        return self.response_data


@pytest.fixture
def mock_openai_model() -> MockLLMModel:
    """Create a mock OpenAI model."""
    return MockLLMModel()


@pytest.fixture
def crisis_message() -> str:
    """Create a crisis message for testing guardrails."""
    return "I don't want to be here anymore. I've been thinking about ending it all."


@pytest.fixture
def safe_message() -> str:
    """Create a safe message for testing."""
    return "I had a good day today. I went for a walk and felt peaceful."


@pytest.fixture
def stressed_message() -> str:
    """Create a stressed but safe message."""
    return "I'm feeling really overwhelmed with everything going on. I just need to vent."
