"""Basic tests for the TTS service."""

import tempfile
import wave

import numpy as np
import pytest

from tts_gateway.providers.mock import MockProvider


def test_mock_provider():
    """Test that the mock provider generates valid WAV data."""
    provider = MockProvider()

    # Test basic synthesis
    audio_data = provider.synthesize("Hello, world!")

    # Should return non-empty bytes
    assert isinstance(audio_data, bytes)
    assert len(audio_data) > 0

    # Should be valid WAV data
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        f.write(audio_data)
        f.flush()

        # Verify it's a valid WAV file
        with wave.open(f.name, "rb") as wav_file:
            assert wav_file.getnchannels() == 1  # Mono
            assert wav_file.getsampwidth() == 2  # 16-bit
            assert wav_file.getframerate() in [8000, 16000, 22050, 44100, 48000]

            # Should have some audio data
            n_frames = wav_file.getnframes()
            assert n_frames > 0

            # Read the audio data
            frames = wav_file.readframes(n_frames)
            audio = np.frombuffer(frames, dtype=np.int16)

            # Should have some non-zero samples
            assert np.any(audio != 0)


def test_mock_provider_deterministic():
    """Test that the mock provider generates the same output for the same input."""
    provider = MockProvider()

    # Generate audio twice with the same seed
    audio1 = provider.synthesize("Test deterministic output", seed=42)
    audio2 = provider.synthesize("Test deterministic output", seed=42)

    # Should be identical
    assert audio1 == audio2

    # Different seed should produce different output
    audio3 = provider.synthesize("Test deterministic output", seed=43)
    assert audio1 != audio3

    # Different text should produce different output
    audio4 = provider.synthesize("Different text", seed=42)
    assert audio1 != audio4


if __name__ == "__main__":
    pytest.main(["-v", "test_tts.py"])
