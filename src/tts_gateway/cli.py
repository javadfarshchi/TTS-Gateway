"""Command-line interface for the TTS Gateway."""
import argparse
import sys
from pathlib import Path
from typing import TextIO

from .api.deps import get_provider
from .core.config import get_settings
from .core.models import AudioFormat, TTSRequest


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Command-line interface for the TTS Gateway.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Input group (text or file)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--text",
        type=str,
        help="Text to convert to speech",
    )
    input_group.add_argument(
        "--file",
        type=argparse.FileType("r", encoding="utf-8"),
        help="Path to a text file to convert to speech",
    )

    # Output options
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default="output.wav",
        help="Output file path",
    )

    # TTS options
    parser.add_argument(
        "--provider",
        type=str,
        default=get_settings().DEFAULT_PROVIDER,
        help=f"TTS provider to use (default: {get_settings().DEFAULT_PROVIDER})",
    )
    parser.add_argument(
        "--voice",
        type=str,
        help="Voice to use (provider-specific)",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=get_settings().DEFAULT_LANGUAGE,
        help=f"Language code (default: {get_settings().DEFAULT_LANGUAGE})",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speaking rate (0.5 to 2.0)",
    )
    parser.add_argument(
        "--pitch",
        type=float,
        default=0.0,
        help="Pitch adjustment (-1.0 to 1.0)",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        type=str,
        choices=[fmt.value for fmt in AudioFormat],
        default=AudioFormat.WAV.value,
        help="Output audio format",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for deterministic output",
    )

    # Verbosity
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    return parser.parse_args()


def read_text_file(file: TextIO) -> str:
    """Read text from a file."""
    try:
        return file.read().strip()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Run the TTS CLI."""
    args = parse_args()

    # Read input text
    if args.file:
        text = read_text_file(args.file)
        args.file.close()
    else:
        text = args.text.strip()

    if not text:
        print("Error: No text to synthesize", file=sys.stderr)
        sys.exit(1)

    # Create the TTS request
    request = TTSRequest(
        text=text,
        voice=args.voice,
        lang=args.lang,
        speed=args.speed,
        pitch=args.pitch,
        fmt=AudioFormat(args.fmt),
        seed=args.seed,
    )

    try:
        # Get the provider and synthesize speech
        provider = get_provider(args.provider)

        if args.verbose:
            print(f"Using provider: {provider.__class__.__name__}")
            print(f"Synthesizing: {text[:50]}..." if len(text) > 50 else f"Synthesizing: {text}")

        audio_data = provider.synthesize(
            text=request.text,
            voice=request.voice,
            lang=request.lang,
            speed=request.speed,
            pitch=request.pitch,
            fmt=request.fmt.value,
            seed=request.seed,
        )

        # Write the output file
        output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(audio_data)

        if args.verbose:
            print(f"Wrote {len(audio_data)} bytes to {output_path}")
        else:
            print(str(output_path))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
