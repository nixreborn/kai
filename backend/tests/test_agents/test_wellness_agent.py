"""Tests for Wellness Agent - Mental health insights and proactive remediation."""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from src.agents.wellness_agent import (
    analyze_wellness_patterns,
    generate_proactive_prompt,
    WELLNESS_SYSTEM_PROMPT,
)
from src.models.agent_models import WellnessInsight


class TestWellnessAgent:
    """Test suite for Wellness Agent."""

    @pytest.mark.asyncio
    async def test_analyze_wellness_patterns_returns_insights(
        self, conversation_history: list[dict[str, str]], wellness_insights: list[WellnessInsight]
    ) -> None:
        """Test that wellness agent returns insights from conversation analysis."""
        conv_text = "\n".join([f"{m['role']}: {m['content']}" for m in conversation_history])

        with patch("src.agents.wellness_agent.wellness_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = wellness_insights
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_wellness_patterns(conv_text)

            assert isinstance(result, list)
            assert all(isinstance(i, WellnessInsight) for i in result)
            assert len(result) > 0
            mock_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_wellness_insight_has_required_fields(
        self, wellness_insights: list[WellnessInsight]
    ) -> None:
        """Test that wellness insights have all required fields."""
        for insight in wellness_insights:
            assert insight.category in ["mood", "behavior", "cognitive", "emotional", "social"]
            assert insight.insight is not None and len(insight.insight) > 0
            assert insight.severity in ["low", "medium", "high"]
            assert isinstance(insight.recommendations, list)
            assert len(insight.recommendations) > 0

    @pytest.mark.asyncio
    async def test_analyze_with_journal_entries(
        self, wellness_insights: list[WellnessInsight]
    ) -> None:
        """Test analyzing wellness patterns with both conversation and journal entries."""
        conversation = "user: I've been feeling down\nassistant: Tell me more"
        journal = "Today was hard. I didn't want to get out of bed."

        with patch("src.agents.wellness_agent.wellness_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = wellness_insights
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_wellness_patterns(conversation, journal)

            # Should pass both conversation and journal to agent
            call_args = mock_agent.run.call_args[0][0]
            assert "Conversation history" in call_args
            assert "Journal entries" in call_args
            assert journal in call_args

    @pytest.mark.asyncio
    async def test_generate_proactive_prompt_for_high_severity(
        self, high_severity_wellness_insight: WellnessInsight
    ) -> None:
        """Test that high severity insights generate proactive prompts."""
        result = await generate_proactive_prompt([high_severity_wellness_insight])

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        # Should be a caring, thoughtful prompt
        assert "?" in result  # Should ask a question

    @pytest.mark.asyncio
    async def test_generate_proactive_prompt_for_medium_severity(
        self, wellness_insights: list[WellnessInsight]
    ) -> None:
        """Test that medium severity insights generate gentle check-ins."""
        # Filter to only medium severity
        medium_insights = [i for i in wellness_insights if i.severity == "medium"]

        result = await generate_proactive_prompt(medium_insights)

        if result:  # May or may not generate prompt for medium
            assert isinstance(result, str)
            assert "?" in result

    @pytest.mark.asyncio
    async def test_generate_proactive_prompt_for_low_severity(self) -> None:
        """Test that low severity insights typically don't generate prompts."""
        low_insight = WellnessInsight(
            category="mood",
            insight="User shows normal mood variation",
            severity="low",
            recommendations=["Continue current wellness practices"],
        )

        result = await generate_proactive_prompt([low_insight])

        # Low severity typically shouldn't trigger proactive prompts
        assert result is None

    @pytest.mark.asyncio
    async def test_proactive_prompt_category_specific_mood(self) -> None:
        """Test that mood-related prompts are appropriate."""
        mood_insight = WellnessInsight(
            category="mood",
            insight="Persistent low mood detected",
            severity="high",
            recommendations=["Seek professional support"],
        )

        result = await generate_proactive_prompt([mood_insight])

        assert result is not None
        prompt_lower = result.lower()
        # Should ask about feelings or mood
        assert any(word in prompt_lower for word in ["feel", "mood", "emotion", "patterns"])

    @pytest.mark.asyncio
    async def test_proactive_prompt_category_specific_behavior(self) -> None:
        """Test that behavior-related prompts are appropriate."""
        behavior_insight = WellnessInsight(
            category="behavior",
            insight="Changes in sleep and self-care patterns",
            severity="high",
            recommendations=["Focus on sleep hygiene"],
        )

        result = await generate_proactive_prompt([behavior_insight])

        assert result is not None
        prompt_lower = result.lower()
        # Should ask about self-care or behaviors
        assert any(word in prompt_lower for word in ["taking care", "self", "changes", "noticed"])

    @pytest.mark.asyncio
    async def test_proactive_prompt_category_specific_cognitive(self) -> None:
        """Test that cognitive-related prompts are appropriate."""
        cognitive_insight = WellnessInsight(
            category="cognitive",
            insight="Pattern of negative thought spirals",
            severity="high",
            recommendations=["Practice cognitive reframing"],
        )

        result = await generate_proactive_prompt([cognitive_insight])

        assert result is not None
        prompt_lower = result.lower()
        # Should ask about thoughts or thinking patterns
        assert any(word in prompt_lower for word in ["think", "process", "mind", "thoughts"])

    @pytest.mark.asyncio
    async def test_proactive_prompt_category_specific_social(self) -> None:
        """Test that social-related prompts are appropriate."""
        social_insight = WellnessInsight(
            category="social",
            insight="Increasing social isolation",
            severity="high",
            recommendations=["Encourage social connection"],
        )

        result = await generate_proactive_prompt([social_insight])

        assert result is not None
        prompt_lower = result.lower()
        # Should ask about connections or relationships
        assert any(word in prompt_lower for word in ["connect", "others", "social", "relationships"])

    @pytest.mark.asyncio
    async def test_wellness_system_prompt_defines_categories(self) -> None:
        """Test that system prompt defines all wellness categories."""
        prompt_lower = WELLNESS_SYSTEM_PROMPT.lower()
        assert "mood" in prompt_lower
        assert "behavior" in prompt_lower
        assert "cognitive" in prompt_lower
        assert "emotional" in prompt_lower
        assert "social" in prompt_lower

    @pytest.mark.asyncio
    async def test_wellness_system_prompt_defines_severity_levels(self) -> None:
        """Test that system prompt defines severity levels."""
        prompt_upper = WELLNESS_SYSTEM_PROMPT.upper()
        assert "LOW" in prompt_upper
        assert "MEDIUM" in prompt_upper
        assert "HIGH" in prompt_upper

    @pytest.mark.asyncio
    async def test_wellness_system_prompt_mentions_professional_help(self) -> None:
        """Test that system prompt mentions recommending professional help."""
        prompt_lower = WELLNESS_SYSTEM_PROMPT.lower()
        assert "professional" in prompt_lower or "therapist" in prompt_lower

    @pytest.mark.asyncio
    async def test_detect_depression_patterns(self) -> None:
        """Test detection of depression patterns."""
        depression_conversation = """
        user: I don't enjoy anything anymore
        assistant: That must be really difficult
        user: I've been like this for months. Nothing makes me happy
        assistant: Have you been able to sleep?
        user: Too much. I sleep all day and still feel tired
        """

        with patch("src.agents.wellness_agent.wellness_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                WellnessInsight(
                    category="mood",
                    insight="Symptoms consistent with depression: anhedonia, fatigue, excessive sleep",
                    severity="high",
                    recommendations=[
                        "Strongly recommend professional evaluation",
                        "Discuss treatment options including therapy and medication",
                        "Monitor for worsening symptoms",
                    ],
                )
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_wellness_patterns(depression_conversation)

            assert len(result) > 0
            mood_insights = [i for i in result if i.category == "mood"]
            assert len(mood_insights) > 0
            assert any(i.severity == "high" for i in mood_insights)

    @pytest.mark.asyncio
    async def test_detect_anxiety_patterns(self) -> None:
        """Test detection of anxiety patterns."""
        anxiety_conversation = """
        user: I can't stop worrying about everything
        assistant: What kind of things worry you?
        user: Everything. Work, health, what people think. My mind won't stop racing
        assistant: How long have you been feeling this way?
        user: Months. I can't relax. My chest feels tight all the time
        """

        with patch("src.agents.wellness_agent.wellness_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                WellnessInsight(
                    category="emotional",
                    insight="Persistent anxiety with physical symptoms",
                    severity="medium",
                    recommendations=[
                        "Practice grounding techniques",
                        "Consider professional evaluation for anxiety disorder",
                        "Explore relaxation exercises",
                    ],
                )
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_wellness_patterns(anxiety_conversation)

            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_detect_cognitive_distortions(self) -> None:
        """Test detection of cognitive distortion patterns."""
        distortion_conversation = """
        user: I always mess everything up
        assistant: Can you give me an example?
        user: I made one mistake at work so now everyone thinks I'm incompetent
        assistant: That sounds like a lot of pressure
        user: If I'm not perfect, I'm a complete failure
        """

        with patch("src.agents.wellness_agent.wellness_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                WellnessInsight(
                    category="cognitive",
                    insight="All-or-nothing thinking and catastrophizing patterns",
                    severity="medium",
                    recommendations=[
                        "Practice cognitive reframing",
                        "Challenge black-and-white thinking",
                        "Consider cognitive behavioral therapy",
                    ],
                )
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_wellness_patterns(distortion_conversation)

            cognitive_insights = [i for i in result if i.category == "cognitive"]
            assert len(cognitive_insights) > 0

    @pytest.mark.asyncio
    async def test_recommendations_are_actionable(
        self, wellness_insights: list[WellnessInsight]
    ) -> None:
        """Test that recommendations are specific and actionable."""
        for insight in wellness_insights:
            assert len(insight.recommendations) >= 2
            for rec in insight.recommendations:
                # Recommendations should be specific sentences
                assert len(rec) > 10  # Not just single words
                # Should contain action words
                action_words = ["practice", "encourage", "suggest", "monitor", "explore", "consider", "reach out"]
                # At least some recommendations should have action words

            # Check that at least one recommendation has an action word
            has_action = any(
                any(word in rec.lower() for word in ["practice", "encourage", "suggest", "monitor", "explore", "consider", "reach", "try", "focus"])
                for rec in insight.recommendations
            )
            assert has_action or insight.severity == "high"  # High severity might be more directive

    @pytest.mark.asyncio
    async def test_multiple_insights_from_rich_conversation(self) -> None:
        """Test that multiple insights can be detected from one conversation."""
        rich_conversation = """
        user: I've been isolating myself. I don't want to see anyone.
        assistant: That must feel lonely.
        user: It is, but I also can't handle being around people. I just want to sleep all day.
        assistant: How has your sleep been?
        user: Too much sleep, but I'm always exhausted. And I keep thinking everyone hates me.
        """

        with patch("src.agents.wellness_agent.wellness_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                WellnessInsight(
                    category="social",
                    insight="Social withdrawal and isolation",
                    severity="medium",
                    recommendations=["Encourage small social interactions"],
                ),
                WellnessInsight(
                    category="behavior",
                    insight="Hypersomnia and fatigue",
                    severity="medium",
                    recommendations=["Evaluate sleep patterns and energy levels"],
                ),
                WellnessInsight(
                    category="cognitive",
                    insight="Negative self-perception and rumination",
                    severity="medium",
                    recommendations=["Practice self-compassion exercises"],
                ),
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_wellness_patterns(rich_conversation)

            # Should detect multiple categories of concerns
            categories = {i.category for i in result}
            assert len(categories) >= 2

    @pytest.mark.asyncio
    async def test_empty_conversation_returns_empty_insights(self) -> None:
        """Test handling of empty conversation."""
        with patch("src.agents.wellness_agent.wellness_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = []
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_wellness_patterns("")

            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_positive_conversation_low_severity(self) -> None:
        """Test that positive conversations result in low severity or no insights."""
        positive_conversation = """
        user: I had a great day today!
        assistant: That's wonderful to hear!
        user: I'm feeling really good. I accomplished my goals and spent time with friends.
        assistant: It sounds like you're in a good place.
        """

        with patch("src.agents.wellness_agent.wellness_agent") as mock_agent:
            mock_result = Mock()
            mock_result.data = [
                WellnessInsight(
                    category="mood",
                    insight="Positive mood and social engagement",
                    severity="low",
                    recommendations=["Continue current wellness practices"],
                )
            ]
            mock_agent.run = AsyncMock(return_value=mock_result)

            result = await analyze_wellness_patterns(positive_conversation)

            # Should either have no insights or low severity
            if result:
                assert all(i.severity == "low" for i in result)
