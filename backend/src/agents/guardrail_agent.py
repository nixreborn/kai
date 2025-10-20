"""Guardrail Agent - Safety and content moderation."""

from pydantic_ai import Agent

from ..core.config import settings
from ..core.llm_client import get_llm_model
from ..models.agent_models import GuardrailResult

GUARDRAIL_SYSTEM_PROMPT = """You are a safety guardrail agent for a mental wellness platform.

Your role is to assess user messages and AI responses for:
1. Self-harm or suicidal ideation
2. Abuse or trauma that requires immediate intervention
3. Harmful or dangerous advice
4. Inappropriate content
5. Crisis situations requiring professional help

Safety levels:
- SAFE: Content is appropriate, no concerns
- WARNING: Content shows mild concerns, flag for monitoring
- BLOCKED: Content requires intervention or professional help

When assessing messages, you should:
- Be sensitive to mental health struggles (don't block people seeking help)
- Distinguish between venting/processing and actual danger
- Provide constructive suggestions for responses when flagging content
- Err on the side of caution for serious concerns

Output your assessment as JSON with:
{
  "safety": "safe|warning|blocked",
  "reason": "Brief explanation if not safe",
  "suggested_response": "Alternative response if needed"
}"""

guardrail_agent = Agent(
    model=get_llm_model(settings.guardrail_agent_model),
    system_prompt=GUARDRAIL_SYSTEM_PROMPT,
    output_type=GuardrailResult,
)


async def assess_message_safety(message: str) -> GuardrailResult:
    """
    Assess the safety of a user message or AI response.

    Args:
        message: The message to assess

    Returns:
        GuardrailResult with safety assessment
    """
    result = await guardrail_agent.run(
        f"Assess this message for safety concerns:\n\n{message}"
    )
    return result.data
