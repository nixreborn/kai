"""Mental Wellness Agent - Provides mental health insights and proactive remediation."""

from pydantic_ai import Agent

from ..core.config import settings
from ..core.llm_client import get_llm_model
from ..models.agent_models import WellnessInsight

WELLNESS_SYSTEM_PROMPT = """You are a mental wellness specialist agent focused on identifying patterns and providing insights.

Your role is to:
1. Monitor conversation patterns for mental health indicators
2. Identify emotional states and changes over time
3. Provide proactive wellness insights and recommendations
4. Suggest appropriate coping strategies and resources

Mental health categories to assess:
- Mood patterns (depression, anxiety, stress)
- Behavioral changes (sleep, appetite, social withdrawal)
- Cognitive patterns (rumination, catastrophizing, all-or-nothing thinking)
- Emotional regulation (intensity, variability, coping)
- Social connection (isolation, relationships, support)

Severity levels:
- LOW: Normal variation, general wellness tips appropriate
- MEDIUM: Notable concerns, suggest coping strategies and monitoring
- HIGH: Significant concerns, recommend professional support

When providing insights:
- Be compassionate and non-alarming
- Focus on patterns, not isolated incidents
- Provide actionable, practical recommendations
- Suggest professional help when appropriate
- Include water therapy/mindfulness practices when relevant

Output format:
{
  "category": "mood|behavior|cognitive|emotional|social",
  "insight": "Brief description of the pattern observed",
  "severity": "low|medium|high",
  "recommendations": ["List of 2-4 specific, actionable suggestions"]
}"""

wellness_agent = Agent(
    model=get_llm_model(settings.wellness_agent_model),
    system_prompt=WELLNESS_SYSTEM_PROMPT,
    output_type=list[WellnessInsight],
)


async def analyze_wellness_patterns(
    conversation_history: str, journal_entries: str | None = None
) -> list[WellnessInsight]:
    """
    Analyze conversation and journal entries for mental wellness patterns.

    Args:
        conversation_history: Recent conversation messages
        journal_entries: Optional journal entries for deeper analysis

    Returns:
        List of wellness insights with recommendations
    """
    analysis_text = f"Conversation history:\n{conversation_history}"

    if journal_entries:
        analysis_text += f"\n\nJournal entries:\n{journal_entries}"

    result = await wellness_agent.run(
        f"Analyze for mental wellness patterns:\n\n{analysis_text}"
    )
    return result.data


async def generate_proactive_prompt(insights: list[WellnessInsight]) -> str | None:
    """
    Generate a proactive conversation starter based on wellness insights.

    This implements the "Let me ask you a question" feature for proactive remediation.

    Args:
        insights: List of wellness insights

    Returns:
        Proactive question/prompt or None if no significant patterns
    """
    high_severity = [i for i in insights if i.severity == "high"]
    medium_severity = [i for i in insights if i.severity == "medium"]

    if high_severity:
        # Focus on most important insight
        insight = high_severity[0]
        prompts = {
            "mood": "I've noticed some patterns in our conversations lately. How have you been feeling about things?",
            "behavior": "I wanted to check in - I've noticed some changes. How are you taking care of yourself these days?",
            "cognitive": "Can I ask you something? I'm curious about how you've been processing things lately.",
            "emotional": "I've been thinking about our conversations. How would you describe your emotional energy right now?",
            "social": "I wanted to reach out - how have your connections with others been feeling lately?",
        }
        return prompts.get(insight.category)

    if medium_severity:
        # Gentle check-in for medium concerns
        return "Hey, just checking in. What's been on your mind lately?"

    return None
