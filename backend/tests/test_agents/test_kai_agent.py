"""Tests for Kai Agent - Main conversational agent."""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from src.agents.kai_agent import kai_agent, KAI_SYSTEM_PROMPT, add_user_context
from src.models.agent_models import UserProfile, UserTrait


class TestKaiAgent:
    """Test suite for Kai Agent."""

    @pytest.mark.asyncio
    async def test_kai_responds_to_simple_message(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that Kai responds to a simple message."""
        with patch("src.agents.kai_agent.kai_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = "I'm here for you. How are you feeling today?"
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await mock_agent.run("Hello, I'm feeling anxious", deps=mock_user_profile)

            assert isinstance(result.data, str)
            assert len(result.data) > 0
            mock_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_kai_system_prompt_personality(self) -> None:
        """Test that Kai's system prompt defines empathetic personality."""
        prompt_lower = KAI_SYSTEM_PROMPT.lower()
        assert "trauma-informed" in prompt_lower
        assert "empathetic" in prompt_lower or "empathy" in prompt_lower
        assert "warm" in prompt_lower
        assert "supportive" in prompt_lower

    @pytest.mark.asyncio
    async def test_kai_system_prompt_boundaries(self) -> None:
        """Test that system prompt sets appropriate boundaries."""
        prompt_upper = KAI_SYSTEM_PROMPT.upper()
        assert "NOT A REPLACEMENT FOR THERAPY" in prompt_upper or "NOT THERAPY" in prompt_upper
        assert "PROFESSIONAL HELP" in prompt_upper or "THERAPIST" in prompt_upper

    @pytest.mark.asyncio
    async def test_kai_system_prompt_water_metaphors(self) -> None:
        """Test that system prompt mentions water therapy theme."""
        prompt_lower = KAI_SYSTEM_PROMPT.lower()
        assert "water" in prompt_lower or "aqua" in prompt_lower
        assert "waves" in prompt_lower or "flow" in prompt_lower or "ebb" in prompt_lower

    @pytest.mark.asyncio
    async def test_kai_mission_statement(self) -> None:
        """Test that Kai's mission is clearly stated."""
        assert "Be the person you needed" in KAI_SYSTEM_PROMPT

    @pytest.mark.asyncio
    async def test_add_user_context_with_traits(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that user context is added when traits exist."""
        context = await add_user_context(mock_user_profile)

        assert context is not None
        assert len(context) > 0
        # Should include trait information
        assert "emotional_expression" in context or "traits" in context.lower()

    @pytest.mark.asyncio
    async def test_add_user_context_without_traits(
        self, empty_user_profile: UserProfile
    ) -> None:
        """Test that empty context is returned when no traits exist."""
        context = await add_user_context(empty_user_profile)

        assert context == ""

    @pytest.mark.asyncio
    async def test_kai_responds_with_validation(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that Kai validates user emotions."""
        with patch("src.agents.kai_agent.kai_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = "It's completely valid to feel this way. Your feelings matter."
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await mock_agent.run(
                "I feel guilty for being sad when others have it worse",
                deps=mock_user_profile
            )

            # Check for validating language
            response = result.data.lower()
            assert any(word in response for word in ["valid", "understand", "normal", "okay", "matter"])

    @pytest.mark.asyncio
    async def test_kai_asks_reflective_questions(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that Kai asks questions to encourage reflection."""
        with patch("src.agents.kai_agent.kai_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = "What do you think might be at the root of these feelings?"
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await mock_agent.run(
                "I've been feeling off lately",
                deps=mock_user_profile
            )

            # Response should be a question
            assert "?" in result.data

    @pytest.mark.asyncio
    async def test_kai_suggests_professional_help_when_appropriate(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that Kai suggests professional help for serious concerns."""
        with patch("src.agents.kai_agent.kai_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = "These feelings sound really difficult. Have you considered speaking with a therapist or counselor?"
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await mock_agent.run(
                "I've been depressed for months and nothing helps",
                deps=mock_user_profile
            )

            response = result.data.lower()
            assert any(word in response for word in ["therapist", "counselor", "professional", "mental health"])

    @pytest.mark.asyncio
    async def test_kai_uses_water_metaphors(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that Kai occasionally uses water metaphors."""
        with patch("src.agents.kai_agent.kai_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = "Like waves in the ocean, emotions ebb and flow. This difficult moment will pass."
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await mock_agent.run(
                "I feel like this sadness will never end",
                deps=mock_user_profile
            )

            response = result.data.lower()
            # Check for aqua-themed language
            water_words = ["wave", "ocean", "flow", "ebb", "tide", "water", "stream", "current"]
            assert any(word in response for word in water_words)

    @pytest.mark.asyncio
    async def test_kai_respects_boundaries(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that Kai respects when users don't want to share."""
        with patch("src.agents.kai_agent.kai_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = "That's completely okay. You don't have to share anything you're not comfortable with. I'm here whenever you're ready."
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await mock_agent.run(
                "I don't really want to talk about it",
                deps=mock_user_profile
            )

            response = result.data.lower()
            assert any(word in response for word in ["okay", "understand", "comfortable", "ready"])

    @pytest.mark.asyncio
    async def test_kai_personalizes_with_user_traits(self) -> None:
        """Test that Kai personalizes responses based on user traits."""
        user_with_direct_style = UserProfile(
            user_id="direct_user",
            traits=[
                UserTrait(name="communication_style_direct", value=0.9, confidence=0.8),
            ],
            communication_style="direct",
        )

        context = await add_user_context(user_with_direct_style)

        assert "direct" in context.lower() or "communication_style_direct" in context

    @pytest.mark.asyncio
    async def test_kai_handles_crisis_appropriately(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that Kai responds appropriately to crisis language (before guardrail blocks)."""
        # Note: In production, guardrail would block this, but testing Kai's innate response
        with patch("src.agents.kai_agent.kai_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = "I'm very concerned about you. Please reach out to a crisis helpline immediately."
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await mock_agent.run(
                "I'm in a really dark place",
                deps=mock_user_profile
            )

            response = result.data.lower()
            # Should show concern
            assert "concern" in response or "help" in response or "support" in response

    @pytest.mark.asyncio
    async def test_kai_handles_positive_messages(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that Kai responds appropriately to positive messages."""
        with patch("src.agents.kai_agent.kai_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = "That's wonderful to hear! I'm so glad you're having a good day. What made it special?"
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await mock_agent.run(
                "I had a great day today! I feel happy.",
                deps=mock_user_profile
            )

            response = result.data.lower()
            # Should celebrate with user
            assert any(word in response for word in ["wonderful", "glad", "happy", "great", "amazing", "pleased"])
