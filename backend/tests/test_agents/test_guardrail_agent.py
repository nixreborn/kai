"""Tests for Guardrail Agent - Safety and content moderation."""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from src.agents.guardrail_agent import assess_message_safety, GUARDRAIL_SYSTEM_PROMPT
from src.models.agent_models import GuardrailResult, MessageSafety


class TestGuardrailAgent:
    """Test suite for Guardrail Agent."""

    @pytest.mark.asyncio
    async def test_assess_safe_message(
        self, safe_message: str, safe_guardrail_result: GuardrailResult
    ) -> None:
        """Test that safe messages are correctly identified."""
        with patch("src.agents.guardrail_agent.guardrail_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = safe_guardrail_result
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await assess_message_safety(safe_message)

            assert result.safety == MessageSafety.SAFE
            assert result.reason is None
            assert result.suggested_response is None
            mock_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_assess_warning_message(
        self, stressed_message: str, warning_guardrail_result: GuardrailResult
    ) -> None:
        """Test that concerning but not crisis messages trigger warning."""
        with patch("src.agents.guardrail_agent.guardrail_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = warning_guardrail_result
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await assess_message_safety(stressed_message)

            assert result.safety == MessageSafety.WARNING
            assert result.reason is not None
            assert "stressed" in result.reason.lower() or "overwhelmed" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_assess_crisis_message(
        self, crisis_message: str, blocked_guardrail_result: GuardrailResult
    ) -> None:
        """Test that crisis messages are blocked with appropriate response."""
        with patch("src.agents.guardrail_agent.guardrail_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = blocked_guardrail_result
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await assess_message_safety(crisis_message)

            assert result.safety == MessageSafety.BLOCKED
            assert result.reason is not None
            assert result.suggested_response is not None
            # Should suggest crisis resources
            assert "crisis" in result.suggested_response.lower() or "helpline" in result.suggested_response.lower()

    @pytest.mark.asyncio
    async def test_guardrail_prompt_includes_safety_levels(self) -> None:
        """Test that system prompt defines all safety levels."""
        assert "SAFE" in GUARDRAIL_SYSTEM_PROMPT
        assert "WARNING" in GUARDRAIL_SYSTEM_PROMPT
        assert "BLOCKED" in GUARDRAIL_SYSTEM_PROMPT

    @pytest.mark.asyncio
    async def test_guardrail_prompt_mentions_crisis_detection(self) -> None:
        """Test that system prompt includes crisis detection guidelines."""
        prompt_lower = GUARDRAIL_SYSTEM_PROMPT.lower()
        assert "self-harm" in prompt_lower or "suicidal" in prompt_lower
        assert "crisis" in prompt_lower
        assert "professional help" in prompt_lower

    @pytest.mark.asyncio
    async def test_assess_self_harm_content(self) -> None:
        """Test detection of self-harm content."""
        self_harm_messages = [
            "I've been hurting myself and can't stop",
            "I want to cut myself again",
            "Sometimes I think about taking all my pills",
        ]

        with patch("src.agents.guardrail_agent.guardrail_agent") as mock_agent:
            for message in self_harm_messages:
                # Mock a blocked result for self-harm
                mock_result = Mock()
                mock_result.data = GuardrailResult(
                    safety=MessageSafety.BLOCKED,
                    reason="Self-harm content detected requiring immediate intervention",
                    suggested_response="I'm very concerned. Please reach out to a crisis helpline immediately.",
                )
                mock_agent.run = AsyncMock(return_value=mock_result)

                result = await assess_message_safety(message)

                assert result.safety == MessageSafety.BLOCKED
                assert result.suggested_response is not None

    @pytest.mark.asyncio
    async def test_assess_normal_venting(self) -> None:
        """Test that normal venting/processing is not flagged."""
        venting_messages = [
            "I had a really frustrating day at work",
            "I'm annoyed with my friend but I'll get over it",
            "Sometimes I feel sad, but that's normal right?",
        ]

        with patch("src.agents.guardrail_agent.guardrail_agent") as mock_agent:
            for message in venting_messages:
                mock_result = Mock()
                mock_result.data = GuardrailResult(
                    safety=MessageSafety.SAFE,
                    reason=None,
                    suggested_response=None,
                )
                mock_agent.run = AsyncMock(return_value=mock_result)

                result = await assess_message_safety(message)

                assert result.safety in [MessageSafety.SAFE, MessageSafety.WARNING]

    @pytest.mark.asyncio
    async def test_assess_substance_abuse_crisis(self) -> None:
        """Test detection of substance abuse crisis."""
        with patch("src.agents.guardrail_agent.guardrail_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = GuardrailResult(
                safety=MessageSafety.BLOCKED,
                reason="Substance abuse crisis requiring immediate intervention",
                suggested_response="Please seek immediate help from a medical professional or call SAMHSA at 1-800-662-4357",
            )
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await assess_message_safety(
                "I've been using more and more, I think I overdosed last night"
            )

            assert result.safety == MessageSafety.BLOCKED

    @pytest.mark.asyncio
    async def test_assess_domestic_violence(self) -> None:
        """Test detection of domestic violence situations."""
        with patch("src.agents.guardrail_agent.guardrail_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = GuardrailResult(
                safety=MessageSafety.BLOCKED,
                reason="Domestic violence situation requiring immediate support",
                suggested_response="Your safety is important. Please contact the National Domestic Violence Hotline at 1-800-799-7233",
            )
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await assess_message_safety(
                "My partner hurt me again last night and I'm scared"
            )

            assert result.safety == MessageSafety.BLOCKED
            assert result.suggested_response is not None

    @pytest.mark.asyncio
    async def test_empty_message_handling(self) -> None:
        """Test handling of empty messages."""
        with patch("src.agents.guardrail_agent.guardrail_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = GuardrailResult(
                safety=MessageSafety.SAFE,
                reason=None,
                suggested_response=None,
            )
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await assess_message_safety("")

            # Should handle gracefully
            assert isinstance(result, GuardrailResult)

    @pytest.mark.asyncio
    async def test_very_long_message_handling(self) -> None:
        """Test handling of very long messages."""
        long_message = "I'm feeling stressed. " * 500  # Very long message

        with patch("src.agents.guardrail_agent.guardrail_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = GuardrailResult(
                safety=MessageSafety.SAFE,
                reason=None,
                suggested_response=None,
            )
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await assess_message_safety(long_message)

            assert isinstance(result, GuardrailResult)
            mock_agent.run.assert_called_once()
