"""Agent Orchestrator - Coordinates multi-agent interactions."""

import logging
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError

from ..core.llm_client import get_circuit_breaker
from ..models.agent_models import (
    AgentResponse,
    AgentRole,
    MessageSafety,
    UserProfile,
)
from .genetic_agent import analyze_user_traits, update_user_profile
from .guardrail_agent import assess_message_safety
from .kai_agent import kai_agent
from .wellness_agent import analyze_wellness_patterns, generate_proactive_prompt

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multi-agent system for user interactions."""

    def __init__(self) -> None:
        """Initialize the orchestrator."""
        self.conversation_buffer: list[dict[str, str]] = []
        self.last_successful_response: str | None = None
        self.response_cache: dict[str, str] = {}  # Simple cache for similar queries

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
        # Check circuit breaker status
        circuit_breaker = get_circuit_breaker()
        if circuit_breaker.state == "open":
            logger.warning("Circuit breaker is open, using fallback response")
            return self._get_fallback_response(
                user_message,
                "I'm experiencing some technical difficulties right now. "
                "I'm here for you, but my responses might be limited. "
                "If you need immediate support, please reach out to a crisis helpline."
            )

        # Step 1: Safety check with error handling
        try:
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
        except (APITimeoutError, APIConnectionError, APIError) as e:
            logger.error(f"Safety check failed: {e}", exc_info=True)
            # Continue with reduced safety checks - log for monitoring
            safety_result = None

        # Step 2: Get Kai's response with fallback
        try:
            kai_result = await kai_agent.run(user_message, deps=user_profile)
            kai_response = kai_result.data
            self.last_successful_response = kai_response
        except (APITimeoutError, APIConnectionError, APIError) as e:
            logger.error(f"Kai agent failed: {e}", exc_info=True)

            # Try to use cached response or fallback
            kai_response = self._get_cached_or_fallback_response(user_message)

            return AgentResponse(
                agent_role=AgentRole.KAI,
                content=kai_response,
                confidence=0.3,
                metadata={
                    "error": "LLM service temporarily unavailable",
                    "fallback": True,
                    "safety": safety_result.safety.value if safety_result else "unknown",
                },
            )

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

        # Analyze traits if enough conversation history (with error handling)
        if len(self.conversation_buffer) >= 6:
            try:
                conv_text = "\n".join(
                    [f"{m['role']}: {m['content']}" for m in self.conversation_buffer[-6:]]
                )
                new_traits = await analyze_user_traits(conv_text)
                if new_traits:
                    updated_profile = await update_user_profile(user_profile, new_traits)
                    metadata["traits_updated"] = len(new_traits)
                    metadata["user_profile"] = updated_profile.model_dump()
            except Exception as e:
                logger.warning(f"Genetic agent analysis failed: {e}")
                # Continue without trait updates

        # Analyze wellness patterns (with error handling)
        if len(self.conversation_buffer) >= 4:
            try:
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
            except Exception as e:
                logger.warning(f"Wellness agent analysis failed: {e}")
                # Continue without wellness insights

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

    def _get_cached_or_fallback_response(self, user_message: str) -> str:
        """
        Get a cached response or generate a fallback.

        Args:
            user_message: The user's message

        Returns:
            Cached or fallback response string
        """
        # Simple keyword matching for common queries
        message_lower = user_message.lower()

        # Check if we have a similar cached response
        for cached_key, cached_response in self.response_cache.items():
            if cached_key.lower() in message_lower or message_lower in cached_key.lower():
                logger.info("Using cached response for similar query")
                return cached_response

        # Use last successful response if available
        if self.last_successful_response:
            logger.info("Using last successful response as fallback")
            return (
                "I'm experiencing some technical difficulties, but I'm still here for you. "
                "Could you rephrase that or ask something else? "
                "If you need immediate support, please reach out to a crisis helpline."
            )

        # Generic fallback responses based on message type
        if any(word in message_lower for word in ["help", "support", "crisis", "emergency"]):
            return (
                "I'm here to support you, but I'm having technical difficulties right now. "
                "If you need immediate help, please contact:\n"
                "- National Suicide Prevention Lifeline: 988\n"
                "- Crisis Text Line: Text HOME to 741741\n"
                "- Emergency Services: 911"
            )
        if any(word in message_lower for word in ["how", "what", "when", "why"]):
            return (
                "I want to help answer your question, but I'm experiencing technical issues. "
                "Please try again in a moment, or feel free to share what's on your mind."
            )
        return (
            "I hear you, and I'm here for you. I'm having some technical difficulties "
            "at the moment, but please know your feelings matter. "
            "Try reaching out again in a moment, or if urgent, please contact a crisis helpline."
        )

    def _get_fallback_response(self, user_message: str, default_message: str) -> AgentResponse:
        """
        Generate a fallback AgentResponse when LLM is unavailable.

        Args:
            user_message: The user's message
            default_message: Default message to use

        Returns:
            AgentResponse with fallback content
        """
        return AgentResponse(
            agent_role=AgentRole.KAI,
            content=default_message,
            confidence=0.1,
            metadata={
                "fallback": True,
                "circuit_breaker_open": True,
                "error": "LLM service unavailable - circuit breaker open",
            },
        )
