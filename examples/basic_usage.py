"""
Basic usage example for the TTS service.

This script demonstrates how to use the TTS service programmatically.
"""
import os
import time
from pathlib import Path

from tts_gateway.providers.mock import MockProvider


def main():
    # Create a mock TTS provider
    provider = MockProvider()

    # Text to synthesize
    text = "Hello, this is a test of the TTS service."

    print(f"Synthesizing: {text}")

    # Generate speech
    start_time = time.time()
    audio_data = provider.synthesize(
        text=text, voice="test-voice", lang="en", speed=1.0, pitch=0.0, fmt="wav"
    )

    # Calculate generation time
    generation_time = time.time() - start_time

    # Save the audio to a file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "example_tts_output.wav"
    with open(output_file, "wb") as f:
        f.write(audio_data)

    print(f"Generated {len(audio_data)} bytes of audio in {generation_time:.2f} seconds")
    print(f"Audio saved to: {output_file.absolute()}")


if __name__ == "__main__":
    main()
