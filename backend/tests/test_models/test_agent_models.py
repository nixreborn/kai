"""Tests for Pydantic agent models."""

import pytest
from pydantic import ValidationError

from src.models.agent_models import (
    AgentRole,
    MessageSafety,
    UserTrait,
    UserProfile,
    GuardrailResult,
    WellnessInsight,
    AgentMessage,
    AgentResponse,
)


class TestAgentModels:
    """Test suite for agent data models."""

    def test_agent_role_enum_values(self) -> None:
        """Test that AgentRole enum has all expected values."""
        assert AgentRole.KAI == "kai"
        assert AgentRole.GUARDRAIL == "guardrail"
        assert AgentRole.GENETIC == "genetic"
        assert AgentRole.WELLNESS == "wellness"

    def test_message_safety_enum_values(self) -> None:
        """Test that MessageSafety enum has all expected values."""
        assert MessageSafety.SAFE == "safe"
        assert MessageSafety.WARNING == "warning"
        assert MessageSafety.BLOCKED == "blocked"

    def test_user_trait_valid_creation(self) -> None:
        """Test creating a valid UserTrait."""
        trait = UserTrait(
            name="emotional_openness",
            value=0.75,
            confidence=0.80,
        )

        assert trait.name == "emotional_openness"
        assert trait.value == 0.75
        assert trait.confidence == 0.80

    def test_user_trait_value_bounds(self) -> None:
        """Test that UserTrait enforces value bounds (0-1)."""
        # Valid bounds
        UserTrait(name="test", value=0.0, confidence=0.5)
        UserTrait(name="test", value=1.0, confidence=0.5)

        # Invalid bounds
        with pytest.raises(ValidationError):
            UserTrait(name="test", value=-0.1, confidence=0.5)

        with pytest.raises(ValidationError):
            UserTrait(name="test", value=1.1, confidence=0.5)

    def test_user_trait_confidence_bounds(self) -> None:
        """Test that UserTrait enforces confidence bounds (0-1)."""
        # Valid bounds
        UserTrait(name="test", value=0.5, confidence=0.0)
        UserTrait(name="test", value=0.5, confidence=1.0)

        # Invalid bounds
        with pytest.raises(ValidationError):
            UserTrait(name="test", value=0.5, confidence=-0.1)

        with pytest.raises(ValidationError):
            UserTrait(name="test", value=0.5, confidence=1.1)

    def test_user_profile_valid_creation(self) -> None:
        """Test creating a valid UserProfile."""
        profile = UserProfile(
            user_id="user123",
            traits=[
                UserTrait(name="trait1", value=0.7, confidence=0.8),
            ],
            preferences={"theme": "aqua"},
            communication_style="supportive",
        )

        assert profile.user_id == "user123"
        assert len(profile.traits) == 1
        assert profile.preferences["theme"] == "aqua"
        assert profile.communication_style == "supportive"

    def test_user_profile_defaults(self) -> None:
        """Test that UserProfile has sensible defaults."""
        profile = UserProfile(user_id="user123")

        assert profile.traits == []
        assert profile.preferences == {}
        assert profile.communication_style == "supportive"

    def test_guardrail_result_safe(self) -> None:
        """Test creating a safe GuardrailResult."""
        result = GuardrailResult(
            safety=MessageSafety.SAFE,
            reason=None,
            suggested_response=None,
        )

        assert result.safety == MessageSafety.SAFE
        assert result.reason is None
        assert result.suggested_response is None

    def test_guardrail_result_blocked(self) -> None:
        """Test creating a blocked GuardrailResult."""
        result = GuardrailResult(
            safety=MessageSafety.BLOCKED,
            reason="Crisis language detected",
            suggested_response="Please reach out to a crisis helpline.",
        )

        assert result.safety == MessageSafety.BLOCKED
        assert result.reason is not None
        assert result.suggested_response is not None

    def test_wellness_insight_valid_creation(self) -> None:
        """Test creating a valid WellnessInsight."""
        insight = WellnessInsight(
            category="mood",
            insight="User shows signs of low mood",
            severity="medium",
            recommendations=["Encourage gentle activity", "Monitor patterns"],
        )

        assert insight.category == "mood"
        assert insight.insight == "User shows signs of low mood"
        assert insight.severity == "medium"
        assert len(insight.recommendations) == 2

    def test_wellness_insight_defaults(self) -> None:
        """Test WellnessInsight defaults."""
        insight = WellnessInsight(
            category="mood",
            insight="Test insight",
            severity="low",
        )

        assert insight.recommendations == []

    def test_agent_message_valid_creation(self) -> None:
        """Test creating a valid AgentMessage."""
        message = AgentMessage(
            role=AgentRole.KAI,
            content="Hello, how are you?",
            metadata={"timestamp": "2024-01-01"},
        )

        assert message.role == AgentRole.KAI
        assert message.content == "Hello, how are you?"
        assert message.metadata["timestamp"] == "2024-01-01"

    def test_agent_message_defaults(self) -> None:
        """Test AgentMessage defaults."""
        message = AgentMessage(
            role=AgentRole.KAI,
            content="Hello",
        )

        assert message.metadata == {}

    def test_agent_response_valid_creation(self) -> None:
        """Test creating a valid AgentResponse."""
        response = AgentResponse(
            agent_role=AgentRole.KAI,
            content="I'm here for you.",
            confidence=0.85,
            metadata={"safety": "safe"},
        )

        assert response.agent_role == AgentRole.KAI
        assert response.content == "I'm here for you."
        assert response.confidence == 0.85
        assert response.metadata["safety"] == "safe"

    def test_agent_response_confidence_bounds(self) -> None:
        """Test that AgentResponse enforces confidence bounds."""
        # Valid bounds
        AgentResponse(
            agent_role=AgentRole.KAI,
            content="Test",
            confidence=0.0,
        )
        AgentResponse(
            agent_role=AgentRole.KAI,
            content="Test",
            confidence=1.0,
        )

        # Invalid bounds
        with pytest.raises(ValidationError):
            AgentResponse(
                agent_role=AgentRole.KAI,
                content="Test",
                confidence=-0.1,
            )

        with pytest.raises(ValidationError):
            AgentResponse(
                agent_role=AgentRole.KAI,
                content="Test",
                confidence=1.1,
            )

    def test_user_profile_serialization(self) -> None:
        """Test that UserProfile can be serialized to dict."""
        profile = UserProfile(
            user_id="user123",
            traits=[
                UserTrait(name="trait1", value=0.7, confidence=0.8),
            ],
            preferences={"theme": "aqua"},
        )

        profile_dict = profile.model_dump()

        assert profile_dict["user_id"] == "user123"
        assert len(profile_dict["traits"]) == 1
        assert profile_dict["traits"][0]["name"] == "trait1"

    def test_user_profile_deserialization(self) -> None:
        """Test that UserProfile can be created from dict."""
        profile_dict = {
            "user_id": "user123",
            "traits": [
                {"name": "trait1", "value": 0.7, "confidence": 0.8}
            ],
            "preferences": {"theme": "aqua"},
            "communication_style": "supportive",
        }

        profile = UserProfile(**profile_dict)

        assert profile.user_id == "user123"
        assert len(profile.traits) == 1

    def test_wellness_insight_severity_values(self) -> None:
        """Test that wellness insight accepts valid severity values."""
        # All these should be valid
        WellnessInsight(category="mood", insight="test", severity="low", recommendations=[])
        WellnessInsight(category="mood", insight="test", severity="medium", recommendations=[])
        WellnessInsight(category="mood", insight="test", severity="high", recommendations=[])

    def test_wellness_insight_category_values(self) -> None:
        """Test that wellness insight accepts valid category values."""
        categories = ["mood", "behavior", "cognitive", "emotional", "social"]

        for category in categories:
            insight = WellnessInsight(
                category=category,
                insight="test",
                severity="low",
                recommendations=[],
            )
            assert insight.category == category

    def test_agent_response_metadata_flexibility(self) -> None:
        """Test that AgentResponse metadata can hold arbitrary data."""
        response = AgentResponse(
            agent_role=AgentRole.KAI,
            content="Test",
            confidence=0.85,
            metadata={
                "safety": "safe",
                "traits_updated": 3,
                "wellness_insights": [{"category": "mood"}],
                "custom_field": "custom_value",
            },
        )

        assert response.metadata["safety"] == "safe"
        assert response.metadata["traits_updated"] == 3
        assert len(response.metadata["wellness_insights"]) == 1
        assert response.metadata["custom_field"] == "custom_value"

    def test_user_trait_json_compatibility(self) -> None:
        """Test that UserTrait can be converted to/from JSON."""
        import json

        trait = UserTrait(name="test", value=0.75, confidence=0.85)

        # To JSON
        trait_json = trait.model_dump_json()
        assert isinstance(trait_json, str)

        # From JSON
        trait_dict = json.loads(trait_json)
        recreated_trait = UserTrait(**trait_dict)

        assert recreated_trait.name == trait.name
        assert recreated_trait.value == trait.value
        assert recreated_trait.confidence == trait.confidence

    def test_guardrail_result_optional_fields(self) -> None:
        """Test that GuardrailResult optional fields work correctly."""
        # Minimal result
        result1 = GuardrailResult(safety=MessageSafety.SAFE)
        assert result1.reason is None
        assert result1.suggested_response is None

        # Full result
        result2 = GuardrailResult(
            safety=MessageSafety.BLOCKED,
            reason="Crisis detected",
            suggested_response="Seek help",
        )
        assert result2.reason is not None
        assert result2.suggested_response is not None

    def test_user_profile_empty_traits_list(self) -> None:
        """Test that UserProfile handles empty traits list."""
        profile = UserProfile(user_id="user123", traits=[])

        assert isinstance(profile.traits, list)
        assert len(profile.traits) == 0

    def test_user_profile_multiple_traits(self) -> None:
        """Test UserProfile with multiple traits."""
        traits = [
            UserTrait(name="trait1", value=0.7, confidence=0.8),
            UserTrait(name="trait2", value=0.6, confidence=0.7),
            UserTrait(name="trait3", value=0.8, confidence=0.9),
        ]

        profile = UserProfile(user_id="user123", traits=traits)

        assert len(profile.traits) == 3
        assert profile.traits[0].name == "trait1"
        assert profile.traits[1].name == "trait2"
        assert profile.traits[2].name == "trait3"

    def test_wellness_insight_empty_recommendations(self) -> None:
        """Test WellnessInsight with empty recommendations list."""
        insight = WellnessInsight(
            category="mood",
            insight="Test",
            severity="low",
            recommendations=[],
        )

        assert isinstance(insight.recommendations, list)
        assert len(insight.recommendations) == 0
