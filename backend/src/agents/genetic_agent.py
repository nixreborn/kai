"""Genetic Counseling Agent - Manages user trait mapping and AI personalization."""

from pydantic_ai import Agent

from ..core.config import settings
from ..core.llm_client import get_llm_model
from ..models.agent_models import UserProfile, UserTrait

GENETIC_SYSTEM_PROMPT = """You are a genetic counseling agent responsible for building user personality profiles.

Your role is to:
1. Analyze conversation patterns and user responses
2. Identify personality traits and behavioral patterns
3. Map user communication preferences
4. Build a "genetic" profile that helps personalize AI interactions

Traits to identify:
- Communication style (direct, gentle, analytical, emotional)
- Emotional patterns (anxious, calm, variable)
- Reflection depth (surface, moderate, deep)
- Engagement preferences (questions, statements, stories)
- Support needs (validation, advice, listening, action)

For each trait, assess:
- Trait value (0.0 to 1.0)
- Confidence in assessment (0.0 to 1.0)

When analyzing conversations, look for:
- Word choice and tone
- Response length and depth
- Emotional expression
- Question types they respond well to
- Topics they engage with

Provide your analysis as a list of traits with values and confidence scores."""

genetic_agent = Agent(
    model=get_llm_model(settings.genetic_agent_model),
    system_prompt=GENETIC_SYSTEM_PROMPT,
    output_type=list[UserTrait],
)


async def analyze_user_traits(conversation_history: str) -> list[UserTrait]:
    """
    Analyze conversation history to extract user traits.

    Args:
        conversation_history: Recent conversation messages

    Returns:
        List of identified user traits with confidence scores
    """
    result = await genetic_agent.run(
        f"Analyze this conversation and identify user traits:\n\n{conversation_history}"
    )
    return result.data


async def update_user_profile(
    current_profile: UserProfile, new_traits: list[UserTrait]
) -> UserProfile:
    """
    Update user profile with newly identified traits.

    Merges new traits with existing ones, updating values based on confidence.

    Args:
        current_profile: Current user profile
        new_traits: Newly identified traits

    Returns:
        Updated user profile
    """
    trait_map = {t.name: t for t in current_profile.traits}

    for new_trait in new_traits:
        if new_trait.name in trait_map:
            existing = trait_map[new_trait.name]
            # Weight by confidence for averaging
            total_confidence = existing.confidence + new_trait.confidence
            weighted_value = (
                existing.value * existing.confidence + new_trait.value * new_trait.confidence
            ) / total_confidence

            trait_map[new_trait.name] = UserTrait(
                name=new_trait.name,
                value=weighted_value,
                confidence=min(1.0, total_confidence / 2),  # Average confidence, max 1.0
            )
        else:
            trait_map[new_trait.name] = new_trait

    current_profile.traits = list(trait_map.values())
    return current_profile
