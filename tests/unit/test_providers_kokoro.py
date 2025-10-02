"""Unit tests for the Kokoro TTS provider."""
from __future__ import annotations

import io
import wave
from pathlib import Path

import numpy as np
import pytest

from tts_gateway.providers.kokoro import KokoroProvider


class _FakeKokoro:
    """Lightweight stand-in for the real Kokoro ONNX runtime."""

    def __init__(
        self,
        model_path: str,
        voices_path: str,
        espeak_config=None,
        vocab_config=None,
    ) -> None:
        self.model_path = model_path
        self.voices_path = voices_path
        self.espeak_config = espeak_config
        self.vocab_config = vocab_config
        self._voices = ["af_alloy", "af_heart"]
        self.create_calls: list[tuple[str, str, float, str]] = []

    def get_voices(self) -> list[str]:
        return list(self._voices)

    def create(
        self,
        text: str,
        voice: str,
        speed: float = 1.0,
        lang: str = "en-us",
    ) -> tuple[np.ndarray, int]:
        self.create_calls.append((text, voice, speed, lang))
        audio = np.linspace(-0.01, 0.01, num=32, dtype=np.float32)
        return audio, 24000


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"0")


def test_kokoro_provider_synthesize_generates_wav(tmp_path, monkeypatch):
    """Synthesizing audio produces denoised WAV bytes and hits Kokoro API."""
    monkeypatch.setattr("tts_gateway.providers.kokoro.Kokoro", _FakeKokoro)

    model_path = tmp_path / "kokoro.onnx"
    voices_path = tmp_path / "voices.bin"
    _touch(model_path)
    _touch(voices_path)

    provider = KokoroProvider(
        model_path=model_path,
        voices_path=voices_path,
        default_voice="af_alloy",
        default_lang="en-us",
        noise_gate_threshold=0.02,
        enable_normalization=True,
        normalize_target=0.5,
    )

    wav_bytes = provider.synthesize(
        text="Testing the Kokoro provider",
        voice="af_alloy",
        speed=1.25,
        pitch=0.1,
        seed=42,
    )

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.getnchannels() == 1
        assert wav_file.getframerate() == 24000
        frames = wav_file.readframes(wav_file.getnframes())

    samples = np.frombuffer(frames, dtype=np.int16)
    assert samples.size > 0
    assert np.max(np.abs(samples)) == 0  # gated to silence


def test_kokoro_provider_voice_fallback(monkeypatch, tmp_path):
    """Unknown voices fall back to the first available voice."""
    monkeypatch.setattr("tts_gateway.providers.kokoro.Kokoro", _FakeKokoro)
    model_path = tmp_path / "kokoro.onnx"
    voices_path = tmp_path / "voices.bin"
    _touch(model_path)
    _touch(voices_path)

    provider = KokoroProvider(
        model_path=model_path,
        voices_path=voices_path,
        default_voice="af_alloy",
        default_lang="en-us",
    )

    fallback = provider._resolve_voice("non-existent")
    assert fallback == "af_alloy"


def test_kokoro_provider_no_available_voices(monkeypatch, tmp_path):
    """A lack of registered Kokoro voices raises an error."""

    class _VoiceLessKokoro(_FakeKokoro):
        def get_voices(self) -> list[str]:
            return []

    monkeypatch.setattr("tts_gateway.providers.kokoro.Kokoro", _VoiceLessKokoro)
    model_path = tmp_path / "kokoro.onnx"
    voices_path = tmp_path / "voices.bin"
    _touch(model_path)
    _touch(voices_path)

    provider = KokoroProvider(
        model_path=model_path,
        voices_path=voices_path,
        default_voice="af_alloy",
        default_lang="en-us",
    )

    with pytest.raises(ValueError):
        provider._resolve_voice("anything")
