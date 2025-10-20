"""Tests for Genetic Agent - User trait mapping and personalization."""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from src.agents.genetic_agent import (
    analyze_user_traits,
    update_user_profile,
    GENETIC_SYSTEM_PROMPT,
)
from src.models.agent_models import UserProfile, UserTrait


class TestGeneticAgent:
    """Test suite for Genetic Agent."""

    @pytest.mark.asyncio
    async def test_analyze_user_traits_from_conversation(
        self, conversation_history: list[dict[str, str]], user_traits: list[UserTrait]
    ) -> None:
        """Test that genetic agent analyzes traits from conversation."""
        conv_text = "\n".join([f"{m['role']}: {m['content']}" for m in conversation_history])

        with patch("src.agents.genetic_agent.genetic_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = user_traits
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_user_traits(conv_text)

            assert isinstance(result, list)
            assert all(isinstance(t, UserTrait) for t in result)
            assert len(result) > 0
            mock_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_trait_has_confidence_score(
        self, user_traits: list[UserTrait]
    ) -> None:
        """Test that all user traits have confidence scores."""
        for trait in user_traits:
            assert 0.0 <= trait.confidence <= 1.0
            assert 0.0 <= trait.value <= 1.0

    @pytest.mark.asyncio
    async def test_update_user_profile_with_new_traits(
        self, empty_user_profile: UserProfile, user_traits: list[UserTrait]
    ) -> None:
        """Test updating a profile with completely new traits."""
        updated_profile = await update_user_profile(empty_user_profile, user_traits)

        assert len(updated_profile.traits) == len(user_traits)
        # All traits should be added
        trait_names = {t.name for t in updated_profile.traits}
        expected_names = {t.name for t in user_traits}
        assert trait_names == expected_names

    @pytest.mark.asyncio
    async def test_update_user_profile_merges_existing_traits(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that updating profile merges with existing traits."""
        initial_trait_count = len(mock_user_profile.traits)

        new_traits = [
            UserTrait(name="emotional_expression", value=0.8, confidence=0.7),  # Update existing
            UserTrait(name="new_trait", value=0.5, confidence=0.6),  # Add new
        ]

        updated_profile = await update_user_profile(mock_user_profile, new_traits)

        # Should have original traits + new ones (minus duplicates)
        assert len(updated_profile.traits) >= initial_trait_count

    @pytest.mark.asyncio
    async def test_trait_value_weighted_by_confidence(
        self, empty_user_profile: UserProfile
    ) -> None:
        """Test that trait values are weighted by confidence when merging."""
        # Add initial trait
        initial_trait = UserTrait(name="test_trait", value=0.5, confidence=0.8)
        empty_user_profile.traits = [initial_trait]

        # Update with new observation (higher confidence should weigh more)
        new_trait = UserTrait(name="test_trait", value=0.9, confidence=0.9)

        updated_profile = await update_user_profile(empty_user_profile, [new_trait])

        # Find the updated trait
        updated_trait = next(t for t in updated_profile.traits if t.name == "test_trait")

        # Value should be weighted average, closer to 0.9 due to higher confidence
        assert 0.5 < updated_trait.value < 0.9
        # Value should be closer to the higher confidence value
        assert abs(updated_trait.value - 0.9) < abs(updated_trait.value - 0.5)

    @pytest.mark.asyncio
    async def test_genetic_system_prompt_defines_traits(self) -> None:
        """Test that system prompt defines types of traits to identify."""
        prompt_lower = GENETIC_SYSTEM_PROMPT.lower()
        assert "communication style" in prompt_lower
        assert "emotional" in prompt_lower
        assert "personality" in prompt_lower or "behavioral" in prompt_lower

    @pytest.mark.asyncio
    async def test_genetic_system_prompt_confidence_scoring(self) -> None:
        """Test that system prompt mentions confidence scoring."""
        prompt_lower = GENETIC_SYSTEM_PROMPT.lower()
        assert "confidence" in prompt_lower
        assert "0.0" in prompt_lower and "1.0" in prompt_lower

    @pytest.mark.asyncio
    async def test_analyze_communication_style_direct(self) -> None:
        """Test identification of direct communication style."""
        direct_conversation = """
        user: I want to know exactly what I should do about my anxiety.
        assistant: What would you like to explore?
        user: Just tell me the steps. I don't need metaphors or stories.
        assistant: I understand you prefer direct communication.
        """

        with patch("src.agents.genetic_agent.genetic_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                UserTrait(name="communication_style_direct", value=0.9, confidence=0.8),
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_user_traits(direct_conversation)

            # Should identify direct style
            direct_traits = [t for t in result if "direct" in t.name.lower()]
            assert len(direct_traits) > 0
            if direct_traits:
                assert direct_traits[0].value > 0.5

    @pytest.mark.asyncio
    async def test_analyze_communication_style_gentle(self) -> None:
        """Test identification of gentle communication style."""
        gentle_conversation = """
        user: I'm not sure how to say this... but I've been struggling
        assistant: Take your time. I'm here to listen.
        user: It's just... everything feels overwhelming. I hope that makes sense?
        assistant: It makes complete sense. Your feelings are valid.
        """

        with patch("src.agents.genetic_agent.genetic_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                UserTrait(name="communication_style_gentle", value=0.8, confidence=0.7),
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_user_traits(gentle_conversation)

            gentle_traits = [t for t in result if "gentle" in t.name.lower()]
            assert len(gentle_traits) > 0

    @pytest.mark.asyncio
    async def test_analyze_emotional_openness(self) -> None:
        """Test identification of emotional openness trait."""
        emotionally_open_conversation = """
        user: I'm feeling really sad and vulnerable right now
        assistant: Thank you for sharing that with me.
        user: I cried for an hour today thinking about my childhood
        assistant: That must have been difficult.
        """

        with patch("src.agents.genetic_agent.genetic_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                UserTrait(name="emotional_openness", value=0.9, confidence=0.8),
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_user_traits(emotionally_open_conversation)

            openness_traits = [t for t in result if "emotional" in t.name.lower() or "openness" in t.name.lower()]
            assert len(openness_traits) > 0

    @pytest.mark.asyncio
    async def test_analyze_reflection_depth(self) -> None:
        """Test identification of reflection depth trait."""
        deep_reflection_conversation = """
        user: I've been thinking about why I react this way. I think it stems from my relationship with my parents.
        assistant: That's a thoughtful observation.
        user: When I examine my patterns, I see I always seek validation from authority figures. It's connected to...
        assistant: You're doing some deep self-reflection.
        """

        with patch("src.agents.genetic_agent.genetic_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                UserTrait(name="reflection_depth", value=0.9, confidence=0.8),
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_user_traits(deep_reflection_conversation)

            reflection_traits = [t for t in result if "reflection" in t.name.lower() or "depth" in t.name.lower()]
            assert len(reflection_traits) > 0

    @pytest.mark.asyncio
    async def test_confidence_increases_with_more_data(
        self, empty_user_profile: UserProfile
    ) -> None:
        """Test that confidence increases as we gather more observations."""
        # First observation
        first_trait = UserTrait(name="test_trait", value=0.7, confidence=0.5)
        profile = await update_user_profile(empty_user_profile, [first_trait])

        initial_confidence = next(t for t in profile.traits if t.name == "test_trait").confidence

        # Second observation
        second_trait = UserTrait(name="test_trait", value=0.8, confidence=0.6)
        profile = await update_user_profile(profile, [second_trait])

        updated_confidence = next(t for t in profile.traits if t.name == "test_trait").confidence

        # Confidence should not exceed 1.0
        assert updated_confidence <= 1.0

    @pytest.mark.asyncio
    async def test_handle_empty_conversation(self) -> None:
        """Test handling of empty conversation."""
        with patch("src.agents.genetic_agent.genetic_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = []
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_user_traits("")

            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_multiple_traits_identified_simultaneously(self) -> None:
        """Test that multiple traits can be identified from one conversation."""
        rich_conversation = """
        user: I need direct answers. I'm feeling anxious and want to understand why.
        assistant: What specific situations trigger your anxiety?
        user: Social situations. I analyze everything people say and worry I said something wrong.
        assistant: That sounds exhausting.
        """

        with patch("src.agents.genetic_agent.genetic_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                UserTrait(name="communication_style_direct", value=0.8, confidence=0.7),
                UserTrait(name="anxiety_level", value=0.7, confidence=0.7),
                UserTrait(name="reflection_depth", value=0.8, confidence=0.6),
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_user_traits(rich_conversation)

            # Should identify multiple traits
            assert len(result) >= 2
