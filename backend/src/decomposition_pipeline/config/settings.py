"""
Application configuration and settings management.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # API Configuration
    api_title: str = "Decomposition Pipeline API"
    api_version: str = "1.0.0"
    api_description: str = "LangGraph-based problem decomposition and solution generation pipeline"
    debug: bool = False

    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # LLM Configuration
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_llm_provider: str = "anthropic"  # "openai" or "anthropic"
    default_model: str = "claude-3-5-sonnet-20241022"

    # LangGraph Configuration
    checkpoint_db_path: str = "data/checkpoints.db"
    max_iterations: int = 100
    recursion_limit: int = 50

    # Agent Pool Configuration
    max_concurrent_agents: int = 10
    agent_timeout: int = 300  # seconds

    # Human-in-the-Loop Configuration
    require_approval_paradigm: bool = True
    require_approval_technique: bool = True
    require_approval_decomposition: bool = True
    require_approval_solution: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
