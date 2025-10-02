#!/usr/bin/env bash
set -euo pipefail
uvicorn tts_gateway.app:app --reload
