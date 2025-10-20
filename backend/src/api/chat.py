"""Chat endpoints for interacting with Kai."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ..agents.orchestrator import AgentOrchestrator
from ..models.agent_models import AgentResponse, UserProfile
from ..security.rate_limiter import RateLimits, limiter
from ..security.validators import sanitize_input, validate_chat_message

router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory storage for demo (replace with database in production)
user_profiles: dict[str, UserProfile] = {}
orchestrators: dict[str, AgentOrchestrator] = {}


class ChatRequest(BaseModel):
    """Chat request from user."""

    user_id: str = Field(description="User identifier")
    message: str = Field(description="User message", min_length=1)
    conversation_history: list[dict[str, str]] | None = Field(
        default=None, description="Optional conversation history"
    )


class ChatResponse(BaseModel):
    """Chat response from Kai."""

    response: str = Field(description="Kai's response")
    metadata: dict = Field(description="Additional metadata")


@router.post("", response_model=ChatResponse)
@limiter.limit(RateLimits.CHAT_MESSAGE)
async def chat(request: Request, chat_request: ChatRequest) -> ChatResponse:
    """
    Send a message to Kai and get a response.

    The multi-agent system processes the message:
    1. Guardrail agent checks safety
    2. Kai agent responds
    3. Genetic agent updates user profile
    4. Wellness agent monitors patterns
    """
    # Validate and sanitize chat message
    is_valid, error_msg = validate_chat_message(chat_request.message)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Sanitize message content
    sanitized_message = sanitize_input(chat_request.message, max_length=5000)

    # Get or create user profile
    if chat_request.user_id not in user_profiles:
        user_profiles[chat_request.user_id] = UserProfile(
            user_id=chat_request.user_id,
            communication_style="supportive",
        )

    # Get or create orchestrator
    if chat_request.user_id not in orchestrators:
        orchestrators[chat_request.user_id] = AgentOrchestrator()

    user_profile = user_profiles[chat_request.user_id]
    orchestrator = orchestrators[chat_request.user_id]

    try:
        # Process message through multi-agent system
        agent_response: AgentResponse = await orchestrator.process_message(
            user_message=sanitized_message,
            user_profile=user_profile,
            conversation_history=chat_request.conversation_history,
        )

        # Update user profile if changed
        if "user_profile" in agent_response.metadata:
            user_profiles[chat_request.user_id] = UserProfile(
                **agent_response.metadata["user_profile"]
            )

        return ChatResponse(
            response=agent_response.content,
            metadata={
                "agent_role": agent_response.agent_role.value,
                "confidence": agent_response.confidence,
                **agent_response.metadata,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/proactive/{user_id}", response_model=ChatResponse | None)
@limiter.limit(RateLimits.PROACTIVE_CHECK_IN)
async def get_proactive_check_in(request: Request, user_id: str) -> ChatResponse | None:
    """
    Get a proactive check-in message for the user.

    This implements the "Let me ask you a question" feature.
    """
    if user_id not in user_profiles or user_id not in orchestrators:
        return None

    user_profile = user_profiles[user_id]
    orchestrator = orchestrators[user_id]

    proactive_message = await orchestrator.get_proactive_check_in(user_profile)

    if proactive_message:
        return ChatResponse(
            response=proactive_message,
            metadata={"proactive": True, "agent_role": "kai"},
        )

    return None


@router.delete("/session/{user_id}")
async def clear_session(user_id: str) -> dict[str, str]:
    """Clear conversation history for a user."""
    if user_id in orchestrators:
        orchestrators[user_id].clear_conversation_buffer()

    return {"status": "session cleared", "user_id": user_id}
