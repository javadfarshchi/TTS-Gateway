"""Kokoro TTS provider implementation."""

from __future__ import annotations

import io
import logging
import wave
from pathlib import Path

import numpy as np
from kokoro_onnx import Kokoro
from kokoro_onnx.config import DEFAULT_VOCAB, SAMPLE_RATE, EspeakConfig
from numpy.typing import NDArray

from .base import TTSProvider

logger = logging.getLogger(__name__)

NDArrayFloat = NDArray[np.float32]


class KokoroProvider(TTSProvider):
    """Text-to-Speech provider backed by the Kokoro ONNX model."""

    def __init__(
        self,
        model_path: str | Path,
        voices_path: str | Path,
        default_voice: str,
        default_lang: str,
        espeak_library: str | None = None,
        espeak_data: str | None = None,
        noise_gate_threshold: float = 0.0,
        enable_normalization: bool = False,
        normalize_target: float = 0.95,
    ) -> None:
        self.model_path = Path(model_path)
        self.voices_path = Path(voices_path)
        self.default_voice = default_voice
        self.default_lang = default_lang
        self.espeak_library = espeak_library
        self.espeak_data = espeak_data
        self.noise_gate_threshold = max(0.0, noise_gate_threshold)
        self.enable_normalization = enable_normalization
        self.normalize_target = max(0.0, min(1.0, normalize_target))

        self._engine: Kokoro | None = None
        self._available_voices: list[str] | None = None

    def _ensure_engine(self) -> Kokoro:
        if self._engine is None:
            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"Kokoro model file not found at {self.model_path}. "
                    "Run `scripts/setup_kokoro.py` to download the assets."
                )

            if not self.voices_path.exists():
                raise FileNotFoundError(
                    f"Kokoro voices file not found at {self.voices_path}. "
                    "Run `scripts/setup_kokoro.py` to download the assets."
                )

            espeak_config = None
            if self.espeak_library or self.espeak_data:
                espeak_config = EspeakConfig(
                    lib_path=self.espeak_library,
                    data_path=self.espeak_data,
                )

            logger.info(
                "Loading Kokoro model from %s (voices: %s)",
                self.model_path,
                self.voices_path,
            )
            self._engine = Kokoro(
                model_path=str(self.model_path),
                voices_path=str(self.voices_path),
                espeak_config=espeak_config,
                vocab_config={"vocab": DEFAULT_VOCAB},
            )
        if self._engine is None:
            raise RuntimeError("Kokoro engine failed to initialize")
        return self._engine

    def _resolve_voice(self, voice: str | None) -> str:
        engine = self._ensure_engine()
        if self._available_voices is None:
            self._available_voices = engine.get_voices()

        candidate = (voice or self.default_voice).strip()
        if candidate in self._available_voices:
            return candidate

        if self._available_voices:
            logger.warning(
                "Voice '%s' not found. Falling back to '%s'. Available voices: %s",
                candidate,
                self._available_voices[0],
                ", ".join(self._available_voices),
            )
            return self._available_voices[0]

        raise ValueError("No Kokoro voices available")

    @staticmethod
    def _normalise_lang(lang: str | None) -> str:
        if not lang:
            return "en-us"
        normalised = lang.replace("_", "-").lower()
        if "-" not in normalised:
            if normalised == "en":
                return "en-us"
            return normalised
        return normalised

    @staticmethod
    def _to_wav(audio: NDArrayFloat, sample_rate: int) -> bytes:
        clipped = np.clip(audio, -1.0, 1.0)
        pcm = (clipped * 32767).astype(np.int16)
        with io.BytesIO() as buffer:
            with wave.open(buffer, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm.tobytes())
            return buffer.getvalue()

    def _post_process(self, audio: NDArrayFloat) -> NDArrayFloat:
        processed = np.copy(audio)

        if self.noise_gate_threshold > 0.0:
            mask = np.abs(processed) < self.noise_gate_threshold
            processed[mask] = 0.0

        if self.enable_normalization:
            peak = float(np.max(np.abs(processed)))
            if peak > 0.0:
                processed = processed * (self.normalize_target / peak)

        return processed

    def synthesize(
        self,
        text: str,
        voice: str | None = None,
        lang: str | None = "en-us",
        speed: float = 1.0,
        pitch: float = 0.0,
        fmt: str = "wav",
        seed: int | None = None,
    ) -> bytes:
        if fmt.lower() != "wav":
            raise ValueError("Kokoro provider currently supports only WAV output.")

        if pitch not in (0.0, None):
            logger.warning(
                "Kokoro provider does not support pitch adjustment; ignoring value %s",
                pitch,
            )

        if seed is not None:
            logger.debug("Kokoro provider ignores seed parameter (%s)", seed)

        engine = self._ensure_engine()
        selected_voice = self._resolve_voice(voice)
        selected_lang = self._normalise_lang(lang or self.default_lang)

        audio, sample_rate = engine.create(
            text=text,
            voice=selected_voice,
            speed=float(speed),
            lang=selected_lang,
        )
        processed_audio = self._post_process(audio)
        return self._to_wav(processed_audio, sample_rate or SAMPLE_RATE)

    @property
    def sample_rate(self) -> int:
        """Return the Kokoro sample rate."""
        return SAMPLE_RATE
