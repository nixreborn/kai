"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # FastAPI Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: str = "http://localhost:3000"

    # LLM Configuration
    llm_base_url: str = "http://192.168.1.7:8000/v1"
    llm_api_key: str = "optional-api-key"
    llm_model: str = "default"

    # Database Configuration
    database_url: str = "postgresql+asyncpg://kai:kai@localhost:5432/kai_db"

    # Security
    secret_key: str = "changeme-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Agent Configuration
    kai_agent_model: str = "default"
    guardrail_agent_model: str = "default"
    genetic_agent_model: str = "default"
    wellness_agent_model: str = "default"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
