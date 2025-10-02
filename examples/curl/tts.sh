#!/usr/bin/env bash
set -euo pipefail

curl -s -X POST "http://localhost:8000/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from Kokoro TTS","provider":"mock"}' \
  --output out.wav

echo "Wrote out.wav"
