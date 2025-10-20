"""Tests for Agent Orchestrator - Multi-agent coordination."""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from src.agents.orchestrator import AgentOrchestrator
from src.models.agent_models import (
    UserProfile,
    MessageSafety,
    GuardrailResult,
    AgentRole,
    WellnessInsight,
    UserTrait,
)


class TestAgentOrchestrator:
    """Test suite for Agent Orchestrator."""

    @pytest.fixture
    def orchestrator(self) -> AgentOrchestrator:
        """Create a fresh orchestrator for each test."""
        return AgentOrchestrator()

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(
        self, orchestrator: AgentOrchestrator
    ) -> None:
        """Test that orchestrator initializes correctly."""
        assert orchestrator.conversation_buffer == []

    @pytest.mark.asyncio
    async def test_process_safe_message_returns_kai_response(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
        safe_message: str,
    ) -> None:
        """Test that safe messages get processed and return Kai's response."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai:

            # Mock guardrail - message is safe
            mock_guardrail.return_value = GuardrailResult(
                safety=MessageSafety.SAFE,
                reason=None,
                suggested_response=None,
            )

            # Mock Kai's response
            mock_kai_result = Mock()
            mock_kai_result.data = "I'm here for you. How can I support you today?"
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            response = await orchestrator.process_message(
                safe_message,
                mock_user_profile
            )

            assert response.agent_role == AgentRole.KAI
            assert response.content == mock_kai_result.data
            assert response.metadata["safety"] == "safe"

    @pytest.mark.asyncio
    async def test_process_blocked_message_returns_guardrail_response(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
        crisis_message: str,
    ) -> None:
        """Test that blocked messages return guardrail response without calling Kai."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai:

            # Mock guardrail - message is blocked
            mock_guardrail.return_value = GuardrailResult(
                safety=MessageSafety.BLOCKED,
                reason="Crisis language detected",
                suggested_response="Please reach out to a crisis helpline immediately: 988",
            )

            response = await orchestrator.process_message(
                crisis_message,
                mock_user_profile
            )

            # Should return guardrail response, not call Kai
            assert response.agent_role == AgentRole.GUARDRAIL
            assert response.metadata["safety"] == "blocked"
            assert response.metadata["crisis"] is True
            assert "crisis" in response.content.lower() or "helpline" in response.content.lower()

            # Kai should not be called
            mock_kai.run.assert_not_called()

    @pytest.mark.asyncio
    async def test_conversation_buffer_updates(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
        safe_message: str,
    ) -> None:
        """Test that conversation buffer is updated with each interaction."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai:

            mock_guardrail.return_value = GuardrailResult(safety=MessageSafety.SAFE)
            mock_kai_result = Mock()
            mock_kai_result.data = "I understand."
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            await orchestrator.process_message(safe_message, mock_user_profile)

            assert len(orchestrator.conversation_buffer) == 2
            assert orchestrator.conversation_buffer[0]["role"] == "user"
            assert orchestrator.conversation_buffer[0]["content"] == safe_message
            assert orchestrator.conversation_buffer[1]["role"] == "assistant"
            assert orchestrator.conversation_buffer[1]["content"] == "I understand."

    @pytest.mark.asyncio
    async def test_conversation_buffer_limited_to_20_messages(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
    ) -> None:
        """Test that conversation buffer doesn't grow beyond 20 messages."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai:

            mock_guardrail.return_value = GuardrailResult(safety=MessageSafety.SAFE)
            mock_kai_result = Mock()
            mock_kai_result.data = "Response"
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            # Add 15 exchanges (30 messages)
            for i in range(15):
                await orchestrator.process_message(f"Message {i}", mock_user_profile)

            # Should be capped at 20
            assert len(orchestrator.conversation_buffer) == 20

    @pytest.mark.asyncio
    async def test_genetic_agent_analyzes_after_threshold(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
    ) -> None:
        """Test that genetic agent analyzes traits after 6 messages."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai, \
             patch("src.agents.orchestrator.analyze_user_traits") as mock_genetic, \
             patch("src.agents.orchestrator.update_user_profile") as mock_update:

            mock_guardrail.return_value = GuardrailResult(safety=MessageSafety.SAFE)
            mock_kai_result = Mock()
            mock_kai_result.data = "Response"
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            new_traits = [UserTrait(name="test_trait", value=0.7, confidence=0.8)]
            mock_genetic.return_value = new_traits

            updated_profile = UserProfile(
                user_id=mock_user_profile.user_id,
                traits=new_traits,
            )
            mock_update.return_value = updated_profile

            # Send 3 messages (6 total in buffer with responses)
            for i in range(3):
                response = await orchestrator.process_message(f"Message {i}", mock_user_profile)

            # After 3rd message, should have 6 messages in buffer
            # Should trigger genetic analysis
            mock_genetic.assert_called()
            assert "traits_updated" in response.metadata

    @pytest.mark.asyncio
    async def test_wellness_agent_analyzes_after_threshold(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
    ) -> None:
        """Test that wellness agent analyzes patterns after 4 messages."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai, \
             patch("src.agents.orchestrator.analyze_wellness_patterns") as mock_wellness:

            mock_guardrail.return_value = GuardrailResult(safety=MessageSafety.SAFE)
            mock_kai_result = Mock()
            mock_kai_result.data = "Response"
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            wellness_insights = [
                WellnessInsight(
                    category="mood",
                    insight="User shows positive mood",
                    severity="low",
                    recommendations=["Continue current practices"],
                )
            ]
            mock_wellness.return_value = wellness_insights

            # Send 2 messages (4 total in buffer)
            for i in range(2):
                response = await orchestrator.process_message(f"Message {i}", mock_user_profile)

            # Should trigger wellness analysis
            mock_wellness.assert_called()
            assert "wellness_insights" in response.metadata

    @pytest.mark.asyncio
    async def test_proactive_prompt_generated_for_high_severity(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
    ) -> None:
        """Test that proactive prompts are generated for high severity insights."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai, \
             patch("src.agents.orchestrator.analyze_wellness_patterns") as mock_wellness, \
             patch("src.agents.orchestrator.generate_proactive_prompt") as mock_proactive:

            mock_guardrail.return_value = GuardrailResult(safety=MessageSafety.SAFE)
            mock_kai_result = Mock()
            mock_kai_result.data = "Response"
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            high_severity_insight = WellnessInsight(
                category="mood",
                insight="Persistent low mood",
                severity="high",
                recommendations=["Seek professional help"],
            )
            mock_wellness.return_value = [high_severity_insight]
            mock_proactive.return_value = "I've noticed some patterns. How are you feeling?"

            # Send 2 messages to trigger wellness analysis
            for i in range(2):
                response = await orchestrator.process_message(f"Message {i}", mock_user_profile)

            # Should generate proactive prompt
            assert "proactive_prompt" in response.metadata
            assert response.metadata["proactive_prompt"] == "I've noticed some patterns. How are you feeling?"

    @pytest.mark.asyncio
    async def test_get_proactive_check_in_with_insufficient_data(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
    ) -> None:
        """Test that proactive check-in returns None with insufficient conversation."""
        result = await orchestrator.get_proactive_check_in(mock_user_profile)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_proactive_check_in_with_sufficient_data(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
    ) -> None:
        """Test that proactive check-in generates message with sufficient data."""
        # Manually populate conversation buffer
        orchestrator.conversation_buffer = [
            {"role": "user", "content": "I'm feeling down"},
            {"role": "assistant", "content": "Tell me more"},
            {"role": "user", "content": "I can't sleep"},
            {"role": "assistant", "content": "That sounds difficult"},
        ]

        with patch("src.agents.orchestrator.analyze_wellness_patterns") as mock_wellness, \
             patch("src.agents.orchestrator.generate_proactive_prompt") as mock_proactive:

            mock_wellness.return_value = [
                WellnessInsight(
                    category="mood",
                    insight="Low mood detected",
                    severity="medium",
                    recommendations=["Monitor patterns"],
                )
            ]
            mock_proactive.return_value = "How have you been feeling lately?"

            result = await orchestrator.get_proactive_check_in(mock_user_profile)

            assert result == "How have you been feeling lately?"

    @pytest.mark.asyncio
    async def test_clear_conversation_buffer(
        self, orchestrator: AgentOrchestrator
    ) -> None:
        """Test that conversation buffer can be cleared."""
        orchestrator.conversation_buffer = [
            {"role": "user", "content": "Test"},
            {"role": "assistant", "content": "Response"},
        ]

        orchestrator.clear_conversation_buffer()

        assert orchestrator.conversation_buffer == []

    @pytest.mark.asyncio
    async def test_multiple_users_separate_contexts(
        self, mock_user_profile: UserProfile
    ) -> None:
        """Test that different orchestrators maintain separate contexts."""
        orchestrator1 = AgentOrchestrator()
        orchestrator2 = AgentOrchestrator()

        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai:

            mock_guardrail.return_value = GuardrailResult(safety=MessageSafety.SAFE)
            mock_kai_result = Mock()
            mock_kai_result.data = "Response"
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            await orchestrator1.process_message("User 1 message", mock_user_profile)
            await orchestrator2.process_message("User 2 message", mock_user_profile)

            # Each should have separate conversation history
            assert len(orchestrator1.conversation_buffer) == 2
            assert len(orchestrator2.conversation_buffer) == 2
            assert orchestrator1.conversation_buffer[0]["content"] == "User 1 message"
            assert orchestrator2.conversation_buffer[0]["content"] == "User 2 message"

    @pytest.mark.asyncio
    async def test_warning_messages_still_processed(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
        stressed_message: str,
    ) -> None:
        """Test that WARNING level messages are still processed (not blocked)."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai:

            mock_guardrail.return_value = GuardrailResult(
                safety=MessageSafety.WARNING,
                reason="User expresses high stress",
                suggested_response=None,
            )

            mock_kai_result = Mock()
            mock_kai_result.data = "I hear that you're stressed. Let's talk about it."
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            response = await orchestrator.process_message(
                stressed_message,
                mock_user_profile
            )

            # Should get Kai's response, not blocked
            assert response.agent_role == AgentRole.KAI
            assert response.metadata["safety"] == "warning"
            # Kai should be called
            mock_kai.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_metadata_includes_all_agent_outputs(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
    ) -> None:
        """Test that response metadata includes outputs from all agents."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai, \
             patch("src.agents.orchestrator.analyze_user_traits") as mock_genetic, \
             patch("src.agents.orchestrator.update_user_profile") as mock_update, \
             patch("src.agents.orchestrator.analyze_wellness_patterns") as mock_wellness, \
             patch("src.agents.orchestrator.generate_proactive_prompt") as mock_proactive:

            mock_guardrail.return_value = GuardrailResult(safety=MessageSafety.SAFE)
            mock_kai_result = Mock()
            mock_kai_result.data = "Response"
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            new_traits = [UserTrait(name="test", value=0.7, confidence=0.8)]
            mock_genetic.return_value = new_traits
            mock_update.return_value = UserProfile(
                user_id=mock_user_profile.user_id,
                traits=new_traits,
            )

            wellness_insights = [
                WellnessInsight(
                    category="mood",
                    insight="Test insight",
                    severity="medium",
                    recommendations=["Test rec"],
                )
            ]
            mock_wellness.return_value = wellness_insights
            mock_proactive.return_value = "Check in question?"

            # Send enough messages to trigger all agents
            for i in range(3):
                response = await orchestrator.process_message(f"Message {i}", mock_user_profile)

            # Check that metadata includes all agent outputs
            assert "safety" in response.metadata
            assert "traits_updated" in response.metadata
            assert "user_profile" in response.metadata
            assert "wellness_insights" in response.metadata
            assert "proactive_prompt" in response.metadata

    @pytest.mark.asyncio
    async def test_confidence_score_in_response(
        self,
        orchestrator: AgentOrchestrator,
        mock_user_profile: UserProfile,
        safe_message: str,
    ) -> None:
        """Test that responses include confidence scores."""
        with patch("src.agents.orchestrator.assess_message_safety") as mock_guardrail, \
             patch("src.agents.orchestrator.kai_agent") as mock_kai:

            mock_guardrail.return_value = GuardrailResult(safety=MessageSafety.SAFE)
            mock_kai_result = Mock()
            mock_kai_result.data = "Response"
            mock_kai.run = AsyncMock(return_value=mock_kai_result)

            response = await orchestrator.process_message(safe_message, mock_user_profile)

            assert hasattr(response, "confidence")
            assert 0.0 <= response.confidence <= 1.0
