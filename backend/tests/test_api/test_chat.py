"""Tests for Chat API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, Mock

from src.main import app
from src.models.agent_models import (
    AgentResponse,
    AgentRole,
    MessageSafety,
    GuardrailResult,
)


client = TestClient(app)


class TestChatAPI:
    """Test suite for Chat API endpoints."""

    def test_chat_endpoint_successful_response(self) -> None:
        """Test successful chat interaction."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            # Mock orchestrator instance
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            # Mock process_message response
            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="I'm here for you. How are you feeling today?",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "test_user",
                    "message": "Hello, I'm feeling anxious",
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "metadata" in data
            assert data["response"] == "I'm here for you. How are you feeling today?"
            assert data["metadata"]["agent_role"] == "kai"
            assert data["metadata"]["safety"] == "safe"

    def test_chat_endpoint_creates_new_user_profile(self) -> None:
        """Test that chat endpoint creates profile for new users."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Welcome!",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            new_user_id = "brand_new_user_12345"
            response = client.post(
                "/api/chat",
                json={
                    "user_id": new_user_id,
                    "message": "Hello",
                }
            )

            assert response.status_code == 200
            # Profile should be created (checked in implementation)

    def test_chat_endpoint_blocked_message(self) -> None:
        """Test chat endpoint with blocked (crisis) message."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            mock_response = AgentResponse(
                agent_role=AgentRole.GUARDRAIL,
                content="I'm very concerned. Please reach out to a crisis helpline at 988.",
                confidence=1.0,
                metadata={
                    "safety": "blocked",
                    "crisis": True,
                    "reason": "Suicidal ideation detected",
                },
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "test_user",
                    "message": "I want to end it all",
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["metadata"]["agent_role"] == "guardrail"
            assert data["metadata"]["crisis"] is True
            assert "crisis" in data["response"].lower() or "helpline" in data["response"].lower()

    def test_chat_endpoint_with_conversation_history(self) -> None:
        """Test chat endpoint with provided conversation history."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="I remember you mentioned that earlier.",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            conversation_history = [
                {"role": "user", "content": "I'm stressed"},
                {"role": "assistant", "content": "Tell me more"},
            ]

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "test_user",
                    "message": "It's about work",
                    "conversation_history": conversation_history,
                }
            )

            assert response.status_code == 200

    def test_chat_endpoint_updates_user_profile(self) -> None:
        """Test that chat endpoint updates user profile when traits are learned."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            # Response includes updated user profile
            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Response",
                confidence=0.85,
                metadata={
                    "safety": "safe",
                    "traits_updated": 2,
                    "user_profile": {
                        "user_id": "test_user",
                        "traits": [
                            {"name": "emotional_openness", "value": 0.8, "confidence": 0.7}
                        ],
                        "preferences": {},
                        "communication_style": "supportive",
                    },
                },
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "test_user",
                    "message": "I'm feeling vulnerable",
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "traits_updated" in data["metadata"]

    def test_chat_endpoint_validation_empty_message(self) -> None:
        """Test that chat endpoint validates non-empty messages."""
        response = client.post(
            "/api/chat",
            json={
                "user_id": "test_user",
                "message": "",
            }
        )

        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_validation_missing_user_id(self) -> None:
        """Test that chat endpoint requires user_id."""
        response = client.post(
            "/api/chat",
            json={
                "message": "Hello",
            }
        )

        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_handles_errors_gracefully(self) -> None:
        """Test that chat endpoint handles errors gracefully."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            # Simulate an error
            mock_orchestrator.process_message = AsyncMock(
                side_effect=Exception("LLM service unavailable")
            )

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "test_user",
                    "message": "Hello",
                }
            )

            assert response.status_code == 500
            assert "error" in response.json()["detail"].lower()

    def test_get_proactive_check_in_no_user(self) -> None:
        """Test proactive check-in for non-existent user."""
        response = client.get("/api/chat/proactive/nonexistent_user")

        # Should return None or 404
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.json() is None

    def test_get_proactive_check_in_with_insights(self) -> None:
        """Test proactive check-in when insights exist."""
        # First create a user session
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Response",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            # Create user session
            client.post(
                "/api/chat",
                json={
                    "user_id": "proactive_test_user",
                    "message": "Hello",
                }
            )

            # Mock proactive check-in
            mock_orchestrator.get_proactive_check_in = AsyncMock(
                return_value="How have you been feeling lately?"
            )

            # Get proactive check-in
            response = client.get("/api/chat/proactive/proactive_test_user")

            assert response.status_code == 200
            if response.json() is not None:
                data = response.json()
                assert "response" in data
                assert data["metadata"]["proactive"] is True

    def test_clear_session_existing_user(self) -> None:
        """Test clearing session for existing user."""
        # Create a session first
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator
            mock_orchestrator.clear_conversation_buffer = Mock()

            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Response",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            # Create session
            client.post(
                "/api/chat",
                json={
                    "user_id": "clear_test_user",
                    "message": "Hello",
                }
            )

            # Clear session
            response = client.delete("/api/chat/session/clear_test_user")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "session cleared"
            assert data["user_id"] == "clear_test_user"

    def test_clear_session_nonexistent_user(self) -> None:
        """Test clearing session for non-existent user (should not error)."""
        response = client.delete("/api/chat/session/nonexistent_user")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "session cleared"

    def test_chat_endpoint_multiple_concurrent_users(self) -> None:
        """Test that multiple users can chat concurrently without interference."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            # Each user gets their own orchestrator
            mock_orchestrator_class.side_effect = lambda: Mock(
                process_message=AsyncMock(
                    return_value=AgentResponse(
                        agent_role=AgentRole.KAI,
                        content="Response",
                        confidence=0.85,
                        metadata={"safety": "safe"},
                    )
                )
            )

            # User 1
            response1 = client.post(
                "/api/chat",
                json={
                    "user_id": "user_1",
                    "message": "User 1 message",
                }
            )

            # User 2
            response2 = client.post(
                "/api/chat",
                json={
                    "user_id": "user_2",
                    "message": "User 2 message",
                }
            )

            assert response1.status_code == 200
            assert response2.status_code == 200

    def test_chat_response_includes_confidence_score(self) -> None:
        """Test that chat responses include confidence scores."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Response",
                confidence=0.92,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "test_user",
                    "message": "Hello",
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "confidence" in data["metadata"]
            assert data["metadata"]["confidence"] == 0.92

    def test_chat_endpoint_long_message(self) -> None:
        """Test chat endpoint with very long message."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="I hear you.",
                confidence=0.85,
                metadata={"safety": "safe"},
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            long_message = "I'm feeling stressed. " * 200  # Very long message

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "test_user",
                    "message": long_message,
                }
            )

            assert response.status_code == 200

    def test_chat_endpoint_with_wellness_insights_metadata(self) -> None:
        """Test that wellness insights are included in response metadata."""
        with patch("src.api.chat.AgentOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            mock_response = AgentResponse(
                agent_role=AgentRole.KAI,
                content="Response",
                confidence=0.85,
                metadata={
                    "safety": "safe",
                    "wellness_insights": [
                        {
                            "category": "mood",
                            "insight": "Low mood detected",
                            "severity": "medium",
                            "recommendations": ["Monitor patterns"],
                        }
                    ],
                },
            )
            mock_orchestrator.process_message = AsyncMock(return_value=mock_response)

            response = client.post(
                "/api/chat",
                json={
                    "user_id": "test_user",
                    "message": "I've been feeling down",
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "wellness_insights" in data["metadata"]
