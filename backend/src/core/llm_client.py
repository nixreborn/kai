"""OpenAI-compatible LLM client configuration."""

from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers import Provider

from .config import settings


class CustomOpenAIProvider(Provider[AsyncOpenAI]):
    """Custom OpenAI provider with custom base URL."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize the provider."""
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    @property
    def client(self) -> AsyncOpenAI:
        """Get the client."""
        return self._client

    @property
    def base_url(self) -> str:
        """Get the base URL."""
        return settings.llm_base_url

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "custom-openai"


def get_llm_model(model_name: str | None = None) -> OpenAIChatModel:
    """
    Get an OpenAI-compatible model instance.

    Args:
        model_name: Optional specific model name to use. Defaults to settings.llm_model.

    Returns:
        OpenAIChatModel configured for the local LLM endpoint.
    """
    # Create custom provider with custom base URL
    provider = CustomOpenAIProvider(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    )

    # Return OpenAI model with the custom provider
    return OpenAIChatModel(
        model_name=model_name or settings.llm_model,
        provider=provider,
    )
