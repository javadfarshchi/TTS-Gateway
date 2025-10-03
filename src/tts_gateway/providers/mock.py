"""Mock TTS provider for testing and development."""

import hashlib
import io
import wave
from typing import cast

import numpy as np
from numpy.typing import NDArray

from .base import TTSProvider

DEFAULT_SAMPLE_RATE = 16000


class MockProvider(TTSProvider):
    """A mock TTS provider that generates simple sine wave audio."""

    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE):
        """Initialize the mock provider.

        Args:
            sample_rate: Sample rate in Hz for the generated audio.
        """
        self.sample_rate = sample_rate

    def _generate_sine_wave(
        self, freq: float, duration: float, volume: float = 0.2, seed: int = 0
    ) -> NDArray[np.float64]:
        """Generate a sine wave with random noise.

        Args:
            freq: Frequency of the sine wave in Hz.
            duration: Duration in seconds.
            volume: Amplitude of the wave (0.0 to 1.0).
            seed: Random seed for reproducibility.

        Returns:
            Mono audio data as a numpy array.
        """
        rng = np.random.default_rng(seed)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        noise = 0.02 * rng.standard_normal(t.shape)
        base_wave = np.sin(2 * np.pi * freq * t)
        signal: NDArray[np.float64] = (volume * base_wave * (1.0 + noise)).astype(
            np.float64, copy=False
        )
        return signal

    def _to_wav_bytes(self, audio: NDArray[np.float64]) -> bytes:
        """Convert mono audio data to WAV format.

        Args:
            audio: Mono audio data as a numpy array.

        Returns:
            WAV file data as bytes.
        """
        # Clip and convert to 16-bit PCM
        clipped = cast(NDArray[np.float64], np.clip(audio, -1.0, 1.0))
        pcm = (clipped * 32767).astype(np.int16).tobytes()

        # Write to in-memory WAV file
        with io.BytesIO() as wav_io:
            with wave.open(wav_io, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(pcm)
            return wav_io.getvalue()

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
        """Generate speech from text using a simple sine wave.

        Args:
            text: The text to synthesize.
            voice: Voice identifier (ignored in mock).
            lang: Language code (affects base frequency).
            speed: Speaking rate (0.5 to 2.0).
            pitch: Pitch adjustment (-1.0 to 1.0).
            fmt: Output format (only 'wav' supported).
            seed: Random seed for reproducibility.

        Returns:
            Audio data in the specified format.
        """
        if fmt.lower() != "wav":
            raise ValueError("Only WAV format is supported by the mock provider")

        # Calculate duration based on text length and speed
        duration = max(0.5, min(5.0, len(text) / 10.0)) / max(0.5, speed)

        # Base frequency depends on text content (deterministic)
        text_hash = int(hashlib.md5(text.encode()).hexdigest(), 16)
        base_freq = 220.0 + (text_hash % 220)  # 220-440 Hz range

        # Adjust frequency based on pitch (-1.0 to 1.0 maps to -12 to +12 semitones)
        freq = base_freq * (2.0 ** (pitch * 12.0 / 12.0))

        # Generate audio
        audio = self._generate_sine_wave(freq=freq, duration=duration, volume=0.2, seed=seed or 0)

        # Convert to WAV
        return self._to_wav_bytes(audio)
