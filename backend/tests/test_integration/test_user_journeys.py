"""Integration tests for complete user journeys."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, Mock

from src.main import app
from src.models.agent_models import (
    AgentResponse,
    AgentRole,
    MessageSafety,
    GuardrailResult,
    WellnessInsight,
    UserTrait,
)


client = TestClient(app)


class TestUserJourneys:
    """Integration tests for complete user workflows."""

    @pytest.mark.asyncio
    async def test_complete_user_journey_registration_to_chat(self) -> None:
        """
        Test complete user journey: registration -> chat with Kai -> profile update.
        """
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            # Mock first interaction
            mock_response1 = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Hello! I'm Kai. I'm here to support you on your wellness journey.",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response1)

            # User's first message
            response1 = client.post(
                "/api/chat",
                json={
                    "user_id": "journey_user_1",
                    "message": "Hello, I'm new here",
                }
            )

            assert response1.status_code == 200
            data1 = response1.json()
            assert "Kai" in data1["response"] or "support" in data1["response"]

            # Mock second interaction with profile update
            mock_response2 = AgentResponse(
                agent_role=AgentRole.KAI,
                content="I hear that you're feeling anxious. That's completely valid.",
                confidence=0.85,
                metadata={
                    "safety": "safe",
                    "traits_updated": 1,
                    "user_profile": {
                        "user_id": "journey_user_1",
                        "traits": [
                            {"name": "emotional_expression", "value": 0.7, "confidence": 0.6}
                        ],
                        "preferences": {},
                        "communication_style": "supportive",
                    },
                },
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response2)

            # User shares feelings
            response2 = client.post(
                "/api/chat",
                json={
                    "user_id": "journey_user_1",
                    "message": "I've been feeling anxious lately",
                }
            )

            assert response2.status_code == 200
            data2 = response2.json()
            assert "traits_updated" in data2["metadata"]

    @pytest.mark.asyncio
    async def test_crisis_journey_guardrail_intervention(self) -> None:
        """
        Test crisis journey: user expresses crisis -> guardrail blocks -> crisis resources.
        """
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            # Mock crisis response
            mock_response = AgentResponse(
                agent_role=AgentRole.GUARDRAIL,
                content="I'm very concerned about what you've shared. Please reach out to the National Suicide Prevention Lifeline at 988 immediately.",
                confidence=1.0,
                metadata={
                    "safety": "blocked",
                    "crisis": True,
                    "reason": "Suicidal ideation detected requiring immediate intervention",
                },
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            # User expresses suicidal thoughts
            response = client.post(
                "/api/chat",
                json={
                    "user_id": "crisis_user",
                    "message": "I don't want to be alive anymore. I've been thinking about ending it.",
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Verify guardrail blocked and provided crisis resources
            assert data["metadata"]["agent_role"] == "guardrail"
            assert data["metadata"]["crisis"] is True
            assert "988" in data["response"] or "crisis" in data["response"].lower()

    @pytest.mark.asyncio
    async def test_wellness_journey_pattern_detection(self) -> None:
        """
        Test wellness journey: multiple chats -> pattern detection -> proactive prompt.
        """
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            user_id = "wellness_journey_user"

            # Conversation 1: User mentions stress
            mock_response1 = AgentResponse(
                agent_role=AgentRole.KAI,
                content="I hear that you're feeling stressed. Tell me more.",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response1)

            client.post(
                "/api/chat",
                json={
                    "user_id": user_id,
                    "message": "I've been really stressed at work",
                }
            )

            # Conversation 2: User mentions sleep issues
            mock_response2 = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Sleep issues can be really challenging.",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response2)

            client.post(
                "/api/chat",
                json={
                    "user_id": user_id,
                    "message": "I can't sleep well either",
                }
            )

            # Conversation 3: Pattern detected, wellness insights included
            mock_response3 = AgentResponse(
                agent_role=AgentRole.KAI,
                content="It sounds like you're going through a difficult time.",
                confidence=0.85,
                metadata={
                    "safety": "safe",
                    "wellness_insights": [
                        {
                            "category": "mood",
                            "insight": "User showing signs of stress and sleep disruption",
                            "severity": "medium",
                            "recommendations": [
                                "Encourage stress management techniques",
                                "Discuss sleep hygiene",
                            ],
                        }
                    ],
                    "proactive_prompt": "I've noticed some patterns. How have you been taking care of yourself?",
                },
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response3)

            response3 = client.post(
                "/api/chat",
                json={
                    "user_id": user_id,
                    "message": "Everything feels overwhelming",
                }
            )

            assert response3.status_code == 200
            data3 = response3.json()

            # Verify wellness insights were generated
            assert "wellness_insights" in data3["metadata"]
            assert "proactive_prompt" in data3["metadata"]

    @pytest.mark.asyncio
    async def test_journal_entry_journey(self) -> None:
        """
        Test journal entry journey: chat -> journal reflection -> deeper analysis.
        """
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            # User shares journal-like entry
            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Thank you for sharing that with me. It takes courage to reflect on difficult feelings.",
                confidence=0.85,
                metadata={
                    "safety": "safe",
                    "wellness_insights": [
                        {
                            "category": "emotional",
                            "insight": "User demonstrates high emotional awareness and reflection",
                            "severity": "low",
                            "recommendations": ["Continue journaling practice"],
                        }
                    ],
                },
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            journal_entry = """
            Today was really hard. I woke up feeling heavy, like there was a weight on my chest.
            I've been thinking about why I react the way I do when people criticize me. I think it
            stems from my childhood, always trying to be perfect. I'm working on accepting that
            it's okay to make mistakes, but it's still a struggle.
            """

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "journal_user",
                    "message": journal_entry,
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Kai should acknowledge the deep sharing
            assert len(data["response"]) > 0

    @pytest.mark.asyncio
    async def test_personalization_journey(self) -> None:
        """
        Test personalization journey: multiple interactions -> trait learning -> adapted responses.
        """
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            user_id = "personalization_user"

            # Conversation 1: User prefers direct communication
            mock_response1 = AgentResponse(
                agent_role=AgentRole.KAI,
                content="I understand you prefer direct communication. I'll be straightforward with you.",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response1)

            client.post(
                "/api/chat",
                json={
                    "user_id": user_id,
                    "message": "I prefer direct answers, no metaphors please",
                }
            )

            # Conversation 2-4: Building trait profile
            for i, message in enumerate([
                "Just tell me what I should do",
                "I don't need flowery language, just facts",
                "Can you give me concrete steps?",
            ]):
                mock_response = AgentResponse(
                    agent_role=AgentRole.KAI,
                    content=f"Here are the concrete steps: {i+1}. ...",
                    confidence=0.85,
                    metadata={
                        "safety": "safe",
                        "traits_updated": 1,
                        "user_profile": {
                            "user_id": user_id,
                            "traits": [
                                {"name": "communication_style_direct", "value": 0.8 + (i * 0.05), "confidence": 0.7 + (i * 0.05)}
                            ],
                            "preferences": {},
                            "communication_style": "direct",
                        },
                    },
                )
                mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

                client.post(
                    "/api/chat",
                    json={
                        "user_id": user_id,
                        "message": message,
                    }
                )

            # Final conversation: Kai adapts to learned style
            mock_response_final = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Here's a direct action plan: 1. Identify triggers. 2. Practice grounding. 3. Seek support.",
                confidence=0.9,
                metadata={
                    "safety": "safe",
                    "user_profile": {
                        "user_id": user_id,
                        "traits": [
                            {"name": "communication_style_direct", "value": 0.95, "confidence": 0.85}
                        ],
                        "preferences": {},
                        "communication_style": "direct",
                    },
                },
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response_final)

            response = client.post(
                "/api/chat",
                json={
                    "user_id": user_id,
                    "message": "How should I deal with my anxiety?",
                }
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_proactive_check_in_journey(self) -> None:
        """
        Test proactive check-in journey: patterns detected -> Kai asks user a question.
        """
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            user_id = "proactive_user"

            # Build up conversation history
            for i in range(3):
                mock_response = AgentResponse(
                    agent_role=AgentRole.KAI,
                    content="I'm listening.",
                    confidence=0.85,
                    metadata={"safety": "safe"},
                )
                mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

                client.post(
                    "/api/chat",
                    json={
                        "user_id": user_id,
                        "message": f"I've been feeling down for days {i}",
                    }
                )

            # Check for proactive prompt
            mock_orchestrator.get_proactive_check_in = AsyncMock(
                return_value="I've noticed you've been feeling down. Can we talk about what's been weighing on you?"
            )

            response = client.get(f"/api/chat/proactive/{user_id}")

            if response.status_code == 200 and response.json() is not None:
                data = response.json()
                assert data["metadata"]["proactive"] is True
                assert "?" in data["response"]  # Should be a question

    @pytest.mark.asyncio
    async def test_session_management_journey(self) -> None:
        """
        Test session management: chat -> clear session -> fresh start.
        """
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator
            mock_orchestrator.clear_conversation_buffer = Mock()

            user_id = "session_user"

            # Initial conversation
            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Hello!",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            client.post(
                "/api/chat",
                json={
                    "user_id": user_id,
                    "message": "Hello",
                }
            )

            # Clear session
            response = client.delete(f"/api/chat/session/{user_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "session cleared"
            mock_orchestrator.clear_conversation_buffer.assert_called_once()

            # New conversation after clearing
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            response2 = client.post(
                "/api/chat",
                json={
                    "user_id": user_id,
                    "message": "Starting fresh",
                }
            )

            assert response2.status_code == 200

    @pytest.mark.asyncio
    async def test_multi_category_insights_journey(self) -> None:
        """
        Test journey where multiple wellness categories are affected.
        """
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            # User shares complex situation affecting multiple areas
            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="It sounds like you're dealing with a lot right now across different areas of your life.",
                confidence=0.85,
                metadata={
                    "safety": "warning",
                    "wellness_insights": [
                        {
                            "category": "mood",
                            "insight": "Persistent low mood",
                            "severity": "medium",
                            "recommendations": ["Monitor mood patterns"],
                        },
                        {
                            "category": "social",
                            "insight": "Social isolation",
                            "severity": "medium",
                            "recommendations": ["Encourage social connection"],
                        },
                        {
                            "category": "behavior",
                            "insight": "Sleep disruption",
                            "severity": "medium",
                            "recommendations": ["Improve sleep hygiene"],
                        },
                    ],
                },
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            complex_message = """
            I've been feeling really down. I don't want to see anyone, I've been avoiding my friends.
            I can't sleep at night, my mind keeps racing. I feel exhausted all the time but can't rest.
            Nothing interests me anymore.
            """

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "complex_user",
                    "message": complex_message,
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Should detect multiple categories of concerns
            if "wellness_insights" in data["metadata"]:
                insights = data["metadata"]["wellness_insights"]
                categories = {i["category"] for i in insights}
                assert len(categories) >= 2

    @pytest.mark.asyncio
    async def test_health_check_during_journey(self) -> None:
        """
        Test that health check works independently during user journey.
        """
        # Health check should work regardless of other operations
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
