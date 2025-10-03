"""Data models for the TTS service."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AudioFormat(str, Enum):
    """Supported audio formats."""

    WAV = "wav"
    MP3 = "mp3"


class TTSRequest(BaseModel):
    """Request model for TTS synthesis."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The text to convert to speech",
        examples=["Hello, world!"],
    )
    voice: str | None = Field(
        None, description="Voice identifier (provider-specific)", examples=["en-US-Wavenet-A"]
    )
    lang: str = Field(
        "en",
        min_length=2,
        max_length=5,
        description="Language code (ISO 639-1)",
        examples=["en", "es", "fr"],
    )
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speaking rate (0.5-2.0)", examples=[1.0])
    pitch: float = Field(
        0.0, ge=-1.0, le=1.0, description="Pitch adjustment (-1.0 to 1.0)", examples=[0.0]
    )
    fmt: AudioFormat = Field(AudioFormat.WAV, description="Output audio format", examples=["wav"])
    seed: int | None = Field(
        None, description="Random seed for deterministic output", examples=[42]
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text input."""
        v = v.strip()
        if not v:
            raise ValueError("Text cannot be empty")
        return v


class TTSResponse(BaseModel):
    """Response model for TTS synthesis."""

    audio: bytes = Field(..., description="Audio data in the requested format")
    format: AudioFormat = Field(..., description="Audio format")
    text: str = Field(..., description="The input text that was synthesized")
    voice: str | None = Field(None, description="Voice used for synthesis")
    sample_rate: int = Field(16000, description="Audio sample rate in Hz")

    class Config:
        """Pydantic config."""

        json_encoders = {bytes: lambda v: "<binary data>"}
