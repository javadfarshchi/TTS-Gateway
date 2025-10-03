"""Base TTS provider interface."""

from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice: str | None = None,
        lang: str | None = "en",
        speed: float = 1.0,
        pitch: float = 0.0,
        fmt: str = "wav",
        seed: int | None = 0,
    ) -> bytes:
        """Synthesize speech from text.

        Args:
            text: The text to synthesize.
            voice: Voice to use (provider-specific).
            lang: Language code (e.g., 'en', 'es', 'fr').
            speed: Speaking rate (0.5 to 2.0).
            pitch: Pitch adjustment (-1.0 to 1.0).
            fmt: Output format ('wav' or 'mp3').
            seed: Random seed for deterministic output.

        Returns:
            Audio data in the specified format.
        """
        raise NotImplementedError
