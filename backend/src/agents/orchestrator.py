"""Agent Orchestrator - Coordinates multi-agent interactions."""

from typing import Any

from ..models.agent_models import (
    AgentResponse,
    AgentRole,
    MessageSafety,
    UserProfile,
    WellnessInsight,
)
from .genetic_agent import analyze_user_traits, update_user_profile
from .guardrail_agent import assess_message_safety
from .kai_agent import kai_agent
from .wellness_agent import analyze_wellness_patterns, generate_proactive_prompt


class AgentOrchestrator:
    """Orchestrates multi-agent system for user interactions."""

    def __init__(self) -> None:
        """Initialize the orchestrator."""
        self.conversation_buffer: list[dict[str, str]] = []

    async def process_message(
        self, user_message: str, user_profile: UserProfile, conversation_history: list[dict[str, str]] | None = None
    ) -> AgentResponse:
        """
        Process a user message through the multi-agent system.

        Flow:
        1. Guardrail agent checks message safety
        2. If safe, Kai responds
        3. Genetic agent analyzes patterns
        4. Wellness agent monitors for insights

        Args:
            user_message: The user's message
            user_profile: Current user profile
            conversation_history: Optional conversation history

        Returns:
            AgentResponse with Kai's reply and metadata
        """
        # Step 1: Safety check
        safety_result = await assess_message_safety(user_message)

        if safety_result.safety == MessageSafety.BLOCKED:
            return AgentResponse(
                agent_role=AgentRole.GUARDRAIL,
                content=safety_result.suggested_response
                or "I'm concerned about what you've shared. Please reach out to a mental health professional or crisis helpline for immediate support.",
                confidence=1.0,
                metadata={
                    "safety": safety_result.safety.value,
                    "reason": safety_result.reason,
                    "crisis": True,
                },
            )

        # Step 2: Get Kai's response
        kai_result = await kai_agent.run(user_message, deps=user_profile)
        kai_response = kai_result.data

        # Add to conversation buffer
        self.conversation_buffer.append({"role": "user", "content": user_message})
        self.conversation_buffer.append({"role": "assistant", "content": kai_response})

        # Keep buffer manageable (last 20 messages)
        if len(self.conversation_buffer) > 20:
            self.conversation_buffer = self.conversation_buffer[-20:]

        # Step 3: Background analysis (async)
        # In production, these would run in background tasks
        metadata: dict[str, Any] = {
            "safety": safety_result.safety.value,
        }

        # Analyze traits if enough conversation history
        if len(self.conversation_buffer) >= 6:
            conv_text = "\n".join(
                [f"{m['role']}: {m['content']}" for m in self.conversation_buffer[-6:]]
            )
            new_traits = await analyze_user_traits(conv_text)
            if new_traits:
                updated_profile = await update_user_profile(user_profile, new_traits)
                metadata["traits_updated"] = len(new_traits)
                metadata["user_profile"] = updated_profile.model_dump()

        # Analyze wellness patterns
        if len(self.conversation_buffer) >= 4:
            conv_text = "\n".join(
                [f"{m['role']}: {m['content']}" for m in self.conversation_buffer[-8:]]
            )
            wellness_insights = await analyze_wellness_patterns(conv_text)
            if wellness_insights:
                metadata["wellness_insights"] = [i.model_dump() for i in wellness_insights]

                # Check if proactive prompt needed
                proactive_prompt = await generate_proactive_prompt(wellness_insights)
                if proactive_prompt:
                    metadata["proactive_prompt"] = proactive_prompt

        return AgentResponse(
            agent_role=AgentRole.KAI,
            content=kai_response,
            confidence=0.85,  # Could be calculated from agent response
            metadata=metadata,
        )

    async def get_proactive_check_in(self, user_profile: UserProfile) -> str | None:
        """
        Generate a proactive check-in message based on user patterns.

        This implements the "Let me ask you a question" feature.

        Args:
            user_profile: Current user profile

        Returns:
            Proactive message or None
        """
        if len(self.conversation_buffer) < 4:
            return None

        conv_text = "\n".join([f"{m['role']}: {m['content']}" for m in self.conversation_buffer])
        wellness_insights = await analyze_wellness_patterns(conv_text)

        if wellness_insights:
            return await generate_proactive_prompt(wellness_insights)

        return None

    def clear_conversation_buffer(self) -> None:
        """Clear the conversation buffer."""
        self.conversation_buffer.clear()
