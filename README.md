# TTS Gateway

[![CI](https://github.com/<your-org>/tts-gateway/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/tts-gateway/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A pluggable Text-to-Speech API gateway built with FastAPI. Route traffic to multiple engines through a single, consistent REST surface.

## Highlights

- Single binary deploy: `uvicorn tts_gateway.app:app` and you are live.
- Pluggable providers: swap in real TTS engines without touching API surfaces.
- Typed models: Pydantic v2 schemas for strong contracts and validation.
- Test ready: unit + integration tests, curl scripts, docker compose.
## Quick start (local)

```bash
git clone https://github.com/<your-org>/tts-gateway.git
cd tts-gateway

# Install developer dependencies + Kokoro runtime
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,kokoro]"

# Download Kokoro ONNX weights & voices
python scripts/setup_kokoro.py

# (Optional) configure overrides
cp env.example .env
vi .env  # adjust KOKORO_* variables if desired

# Launch the gateway
uvicorn tts_gateway.app:app --reload
```

Test the default Kokoro provider:

```bash
curl -X POST "http://localhost:8000/api/v1/tts" \
  -H "Content-Type: application/json" \
  -H "Accept: audio/wav" \
  -d '{"text":"Hello from the Kokoro TTS gateway","voice":"af_alloy"}' \
  --output out.wav
```

### Docker

```bash
docker compose -f docker/compose.yml up --build
```

API docs are served (when `DEBUG=true`) at `http://localhost:8000/docs`.

## API Overview

- `POST /api/v1/tts` — Synthesize audio.
- `GET /api/v1/tts/formats` — List supported output formats.
- `GET /api/v1/healthz` — Service health.

The payload for `POST /api/v1/tts` accepts the schema defined in `tts_gateway/core/models.py` (`TTSRequest`).

## Providers

- **kokoro** *(default)* — High-quality speech powered by Kokoro ONNX.
- **mock** *(included)* — Sine-wave audio for integration testing.
- **piper** *(coming soon)* — Hook into rhasspy/piper voices.

Adding a provider? Implement `tts_gateway.providers.base.TTSProvider` and register it in `tts_gateway/api/deps.py`.

## Examples & Tooling

- `examples/basic_usage.py` — Minimal Python client.
- `examples/curl/tts.sh` — Copy/paste curl helper (writes `out.wav`).
- `scripts/dev.sh` — Run locally (`uvicorn --reload`).
- `scripts/setup_kokoro.py` — Download Kokoro ONNX weights and voices.
- `scripts/test.sh` — Run the full test suite.
- `scripts/lint.sh` — Ruff, Black, Mypy in one go.

## Development Workflow

```bash
pip install -e ".[dev]"
pre-commit install        # one time setup
scripts/lint.sh
scripts/test.sh
```

### Pre-commit

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Running Tests

```bash
PYTHONPATH=src pytest -q
```

## Configuration

- Copy `env.example` to `.env` and override settings as needed. Key Kokoro knobs:
  - `KOKORO_MODEL_PATH` / `KOKORO_VOICES_PATH` — where weights are stored (defaults to `models/kokoro/`).
  - `KOKORO_NOISE_GATE_THRESHOLD` — silence residual hiss below this amplitude.
  - `KOKORO_ENABLE_NORMALIZATION` / `KOKORO_NORMALIZE_TARGET` — control loudness post-processing.
- `docker/compose.yml` builds the image and exposes port 8000.
- Optional provider-specific environment variables live under `tts_gateway/core/config.py`.

## Legal

This repository ships only orchestration code and mock audio. You are responsible for complying with the licenses and usage terms of any third-party voices or providers you integrate.

## Contributing

Pull requests welcome! Please run `scripts/lint.sh` and `scripts/test.sh` (or `pre-commit run --all-files`) before submitting. Check out `CONTRIBUTING.md` for details.

## ⭐️ Enjoying it?

If this project saves you time, please **star the repo** and share it with friends building speech experiences!
