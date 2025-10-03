"""Dependencies for the TTS API."""

import logging

from fastapi import HTTPException, Request, status

from tts_gateway.core.config import get_settings
from tts_gateway.core.models import TTSRequest
from tts_gateway.providers import KokoroProvider, MockProvider, TTSProvider

# Provider registry
_PROVIDER_REGISTRY: dict[str, TTSProvider] = {}
_LOGGER = logging.getLogger(__name__)


def get_provider(provider_name: str | None = None) -> TTSProvider:
    """Get a TTS provider by name.

    Args:
        provider_name: Name of the provider to get. If None, returns the default provider.
        An instance of the requested TTS provider.

    Raises:
        HTTPException: If the requested provider is not found.
    """
    settings = get_settings()
    provider_name = provider_name or settings.DEFAULT_PROVIDER

    if not _PROVIDER_REGISTRY:
        # Initialize default providers if none are registered
        settings = get_settings()

        if settings.DEFAULT_PROVIDER == "kokoro":
            try:
                _PROVIDER_REGISTRY["kokoro"] = KokoroProvider(
                    model_path=settings.KOKORO_MODEL_PATH,
                    voices_path=settings.KOKORO_VOICES_PATH,
                    default_voice=settings.KOKORO_DEFAULT_VOICE,
                    default_lang=settings.KOKORO_DEFAULT_LANG,
                    espeak_library=settings.KOKORO_ESPEAK_LIBRARY,
                    espeak_data=settings.KOKORO_ESPEAK_DATA,
                )
            except FileNotFoundError as exc:
                _LOGGER.warning("Kokoro provider unavailable: %s", exc)
            except Exception as exc:  # noqa: BLE001
                _LOGGER.exception("Failed to initialize Kokoro provider: %s", exc)

        _PROVIDER_REGISTRY.setdefault("mock", MockProvider())

    if provider_name not in _PROVIDER_REGISTRY:
        if provider_name == "kokoro" and "mock" in _PROVIDER_REGISTRY:
            _LOGGER.warning("Falling back to mock provider because Kokoro is unavailable")
            return _PROVIDER_REGISTRY["mock"]

        available = ", ".join(_PROVIDER_REGISTRY.keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{provider_name}' not found. Available providers: {available}",
        )

    return _PROVIDER_REGISTRY[provider_name]


def register_provider(name: str, provider: TTSProvider) -> None:
    """Register a new TTS provider.

    Args:
        name: Name to register the provider under.
        provider: Provider instance to register.
    """
    _PROVIDER_REGISTRY[name] = provider


def validate_tts_request(request: TTSRequest) -> TTSRequest:
    """Validate the TTS request.

    Args:
        request: The TTS request to validate.

    Returns:
        The validated request.

    Raises:
        HTTPException: If the request is invalid.
    """
    settings = get_settings()

    if len(request.text) > settings.MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text too long. Maximum length is {settings.MAX_TEXT_LENGTH} characters.",
        )

    return request


# Dependency for FastAPI
def get_tts_provider(
    request: Request,
) -> TTSProvider:
    """Dependency to get a TTS provider.

    Args:
        request: The FastAPI request object.

    Returns:
        A TTS provider instance.
    """
    provider_name = request.query_params.get("provider")
    return get_provider(provider_name)
