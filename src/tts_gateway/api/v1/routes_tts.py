"""TTS synthesis endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from tts_gateway.api.deps import get_tts_provider, validate_tts_request
from tts_gateway.core.config import get_settings
from tts_gateway.core.models import AudioFormat, TTSRequest, TTSResponse
from tts_gateway.providers import TTSProvider

router = APIRouter(prefix="/tts", tags=["tts"])


@router.post("", response_model=TTSResponse)
async def synthesize(
    request: TTSRequest,
    provider: Annotated[TTSProvider, Depends(get_tts_provider)],
) -> Response:
    """Synthesize speech from text.

    Args:
        request: The TTS request containing the text and parameters.
        provider: The TTS provider to use for synthesis.

    Returns:
        A response containing the synthesized audio.

    Raises:
        HTTPException: If synthesis fails or the request is invalid.
    """
    settings = get_settings()

    try:
        # Validate the request
        request = validate_tts_request(request)

        # Synthesize the speech
        audio_data = provider.synthesize(
            text=request.text,
            voice=request.voice,
            lang=request.lang,
            speed=request.speed,
            pitch=request.pitch,
            fmt=request.fmt.value,
            seed=request.seed,
        )

        # Determine the media type based on the format
        media_type = f"audio/{request.fmt.value}"

        # Create the response
        response = TTSResponse(
            audio=audio_data,
            format=request.fmt,
            text=request.text,
            voice=request.voice or settings.DEFAULT_VOICE,
            sample_rate=settings.DEFAULT_SAMPLE_RATE,
        )

        # Return the audio data directly for streaming
        return Response(
            content=response.audio,
            media_type=media_type,
            headers={
                "X-TTS-Provider": provider.__class__.__name__,
                "X-TTS-Voice": response.voice or "",
                "X-TTS-Language": request.lang,
            },
        )

    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to synthesize speech: {err}",
        ) from err


@router.get("/formats", response_model=dict[str, Any])
async def get_supported_formats() -> dict[str, Any]:
    """Get a list of supported audio formats and their MIME types."""
    return {
        "formats": [{"id": fmt.value, "mime_type": f"audio/{fmt.value}"} for fmt in AudioFormat]
    }
