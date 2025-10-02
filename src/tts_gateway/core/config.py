"""Configuration management for the TTS Gateway service."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application settings
    APP_NAME: str = "TTS Gateway"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = False

    # API settings
    API_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"

    # TTS settings
    DEFAULT_PROVIDER: str = "kokoro"
    DEFAULT_VOICE: str = "af_alloy"
    DEFAULT_LANGUAGE: str = "en-us"
    DEFAULT_SAMPLE_RATE: int = 24000

    # Kokoro provider configuration
    KOKORO_MODEL_PATH: str = "models/kokoro/kokoro-v1.0.onnx"
    KOKORO_VOICES_PATH: str = "models/kokoro/voices-v1.0.bin"
    KOKORO_DEFAULT_VOICE: str = "af_alloy"
    KOKORO_DEFAULT_LANG: str = "en-us"
    KOKORO_ESPEAK_LIBRARY: str | None = None
    KOKORO_ESPEAK_DATA: str | None = None
    KOKORO_NOISE_GATE_THRESHOLD: float = 0.003
    KOKORO_ENABLE_NORMALIZATION: bool = True
    KOKORO_NORMALIZE_TARGET: float = 0.95

    # Audio settings
    MAX_AUDIO_DURATION: int = 600  # seconds
    MAX_TEXT_LENGTH: int = 5000

    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        """Parse CORS origins from environment."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        v = v.upper()
        if v not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {v}")
        return v


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the application settings.

    This function allows for dependency injection in FastAPI routes.
    """
    return settings
