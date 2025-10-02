
# TTS Gateway — Publication Plan

**Goal:** Convert the current POC into a self-contained, well-tested, compliance-friendly TTS service repo (CLI + FastAPI), with clear docs, examples, and CI.

---

## 0) High-level scope

* ✅ Deliverables

  * Python package (`src/` layout), CLI, and FastAPI service
  * Adapters interface + at least 2 providers: `mock` (tone/sine) and `kokoro` (if you have it) or `piper` (local) — optional stub if engine unavailable
  * Deterministic tests (unit + integration)
  * Dockerfile + docker compose
  * README, LEGAL, CONTRIBUTING, CI workflow

* 🚫 Out of scope (v0.1.0)

  * Shipping large proprietary voice assets
  * Cloud-provider creds (documented but not included)

---

## 1) Target directory structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── .pre-commit-config.yaml
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LEGAL_CONSIDERATIONS.md
├── LICENSE
├── README.md
├── docker/
│   ├── Dockerfile
│   └── compose.yml
├── docs/
│   ├── api.md
│   └── architecture.md
├── examples/
│   ├── audio/                      # tiny demo wavs (<200KB each) OR empty with README
│   ├── curl/
│   │   └── tts.sh
│   ├── postman_collection.json
│   └── texts/
│       ├── sample.txt
│       └── long.txt
├── env.example
├── pyproject.toml                  # single source of truth
├── scripts/
│   ├── dev.sh
│   ├── lint.sh
│   └── test.sh
├── src/
│   └── tts_gateway/
│       ├── __init__.py
│       ├── app.py                  # FastAPI app factory
│       ├── cli.py                  # `tts-gateway` CLI entrypoint
│       ├── api/
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── routes_health.py
│       │       └── routes_tts.py   # POST /api/v1/tts
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py           # pydantic-settings
│       │   ├── logging.py
│       │   └── models.py           # pydantic schemas (Request/Response)
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py             # TTSProvider ABC
│       │   ├── mock.py             # deterministic sine-wave generator
│       │   └── kokoro.py           # OPTIONAL: wrapper; or piper.py if preferred
│       └── audio/
│           ├── __init__.py
│           ├── dsp.py              # resample, normalize, concat
│           └── io.py               # write/read WAV/MP3 (wave/soundfile)
└── tests/
    ├── unit/
    │   ├── test_audio_dsp.py
    │   ├── test_models.py
    │   ├── test_providers_mock.py
    │   └── test_cli.py
    ├── integration/
    │   ├── test_api_health.py
    │   └── test_api_tts.py
    └── fixtures/
        ├── texts/
        │   ├── hello.txt
        │   └── long.txt
        └── audio/
            └── golden_sine_1s_16k.wav  # very small; or generate-on-the-fly
```

> Notes:
>
> * Move large WAVs out of the repo. If you must keep samples, keep them tiny or use **Git LFS** with a `.gitattributes` file.
> * Replace `docker-compose.yml` with `docker/compose.yml` for clarity.

---

## 2) Tasks & milestones

### Milestone A — Skeleton & hygiene

* [ ] Create structure above; remove committed `__pycache__` and large WAVs
* [ ] Add `.gitignore`, `.pre-commit-config.yaml`
* [ ] Add `LEGAL_CONSIDERATIONS.md` (no proprietary voices shipped; user-provided models only)
* [ ] Convert to **`pyproject.toml`**; keep `requirements.txt` only if you must (generate from pyproject for Docker)

### Milestone B — Core app

* [ ] `TTSProvider` ABC (`providers/base.py`): `synthesize(text, voice, lang, speed, pitch, format) -> bytes`
* [ ] `mock` provider: deterministic sine wave via NumPy; 16 kHz mono PCM WAV
* [ ] `core/models.py`: `TTSRequest`, `TTSResponse` (base64 or bytes in streaming)
* [ ] `api/v1/routes_tts.py`: `POST /api/v1/tts` (JSON body → audio/wav response)
* [ ] `app.py`: mount router, add `/api/v1/healthz`

### Milestone C — CLI

* [ ] `cli.py` with `argparse` or `typer`

  * `tts --text "Hello" --provider mock --out out.wav`
  * `tts --file examples/texts/sample.txt --voice emma --speed 1.0 --format wav`
* [ ] Register entrypoint in `pyproject.toml` → `tts`

### Milestone D — Audio utils

* [ ] `audio/dsp.py`: `generate_sine(freq=440, secs=1.0, sr=16000)`, `normalize_rms`, `resample`
* [ ] `audio/io.py`: `write_wav(bytes|np.ndarray, sr)`, `read_wav(path)`

### Milestone E — Tests

* **Unit**

  * [ ] `test_audio_dsp.py`: shapes, dtype, RMS normalization, resample
  * [ ] `test_providers_mock.py`: deterministic MD5 of byte output given seed & params
  * [ ] `test_models.py`: pydantic validation (bounds for speed, pitch, format enum)
  * [ ] `test_cli.py`: runs, writes small wav, correct exit code
* **Integration**

  * [ ] `test_api_health.py`: `GET /api/v1/healthz` 200
  * [ ] `test_api_tts.py`: `POST /api/v1/tts` → `200` + `audio/wav` content-type + non-empty body
* **Fixtures**

  * [ ] Tiny `hello.txt`, `long.txt` (few KB)
  * [ ] Golden sine (optional) or generate on the fly inside tests

### Milestone F — Docker & scripts

* [ ] `docker/Dockerfile` (slim, multi-stage optional)
* [ ] `docker/compose.yml` exposing `8000`
* [ ] `scripts/dev.sh` (uvicorn), `scripts/test.sh` (pytest), `scripts/lint.sh` (ruff/black/mypy)

### Milestone G — CI & docs

* [ ] `.github/workflows/ci.yml`: ruff, black, mypy, pytest (Python 3.11)
* [ ] `docs/api.md`: list endpoints; link `http://localhost:8000/docs`
* [ ] `docs/architecture.md`: one diagram + sequence (text → provider → audio)

---

## 3) Key files (stubs Windsurf can implement)

### `src/tts_gateway/providers/base.py`

```python
from abc import ABC, abstractmethod
from typing import Optional

class TTSProvider(ABC):
    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        lang: Optional[str] = "en",
        speed: float = 1.0,
        pitch: float = 0.0,
        fmt: str = "wav",
        seed: Optional[int] = 0,
    ) -> bytes:
        """Return audio bytes in the requested format (default wav)."""
        raise NotImplementedError
```

### `src/tts_gateway/providers/mock.py`

```python
import io, hashlib
import numpy as np
import wave
from .base import TTSProvider

SR = 16000

def _sine(freq: float, secs: float, sr: int = SR, amp: float = 0.2, seed: int = 0):
    rng = np.random.default_rng(seed)
    t = np.arange(int(secs * sr)) / sr
    # text length drives duration; simple deterministic mapping
    y = amp * np.sin(2 * np.pi * freq * t) * (1.0 + 0.02 * rng.standard_normal(t.shape))
    return np.clip(y, -1.0, 1.0).astype(np.float32)

def _to_wav_bytes(x: np.ndarray, sr: int = SR) -> bytes:
    buf = io.BytesIO()
    # 16-bit PCM
    pcm = (x * 32767.0).astype(np.int16).tobytes()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm)
    return buf.getvalue()

class MockProvider(TTSProvider):
    def synthesize(self, text, voice=None, lang="en", speed=1.0, pitch=0.0, fmt="wav", seed=0) -> bytes:
        secs = max(0.5, min(5.0, len(text) / 20.0)) / max(0.5, speed)
        base_freq = 220.0 + (hash(text) % 220)  # deterministic per text
        y = _sine(freq=base_freq + pitch * 50.0, secs=secs, seed=seed)
        return _to_wav_bytes(y)
```

### `src/tts_gateway/core/models.py`

```python
from pydantic import BaseModel, Field, constr
from typing import Optional

class TTSRequest(BaseModel):
    text: constr(min_length=1, max_length=5000)
    provider: str = Field(default="mock", pattern=r"^[a-zA-Z0-9_-]+$")
    voice: Optional[str] = None
    lang: str = "en"
    speed: float = Field(1.0, ge=0.5, le=2.0)
    pitch: float = Field(0.0, ge=-1.0, le=1.0)
    fmt: str = Field("wav", pattern=r"^(wav|mp3)$")
    seed: int = 0
```

### `src/tts_gateway/api/v1/routes_tts.py`

```python
from fastapi import APIRouter, HTTPException, Response
from .. import deps
from ...core.models import TTSRequest

router = APIRouter(prefix="/api/v1", tags=["tts"])

@router.post("/tts")
def synthesize(req: TTSRequest):
    provider = deps.get_provider(req.provider)
    if not provider:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")
    audio = provider.synthesize(
        text=req.text, voice=req.voice, lang=req.lang,
        speed=req.speed, pitch=req.pitch, fmt=req.fmt, seed=req.seed
    )
    media = "audio/wav" if req.fmt == "wav" else "audio/mpeg"
    return Response(content=audio, media_type=media)
```

### `src/tts_gateway/api/deps.py`

```python
from ..providers.mock import MockProvider
# TODO: register additional providers here
_REGISTRY = {
    "mock": MockProvider(),
}

def get_provider(name: str):
    return _REGISTRY.get(name)
```

### `src/tts_gateway/app.py`

```python
from fastapi import FastAPI
from .api.v1.routes_tts import router as tts_router

app = FastAPI(title="TTS Service", version="0.1.0")

@app.get("/api/v1/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(tts_router)
```

### `src/tts_gateway/cli.py`

```python
import argparse, sys
from .api import deps

def main():
    p = argparse.ArgumentParser("tts")
    p.add_argument("--text", help="Text to synthesize")
    p.add_argument("--file", help="Path to text file")
    p.addargument("--provider", default="mock")
    p.add_argument("--out", default="out.wav")
    p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--pitch", type=float, default=0.0)
    p.add_argument("--fmt", default="wav", choices=["wav", "mp3"])
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    text = args.text
    if not text and args.file:
        text = open(args.file, "r", encoding="utf-8").read()
    if not text:
        print("No text provided", file=sys.stderr); sys.exit(2)

    provider = deps.get_provider(args.provider)
    if not provider:
        print(f"Unknown provider: {args.provider}", file=sys.stderr); sys.exit(2)

    audio = provider.synthesize(text, speed=args.speed, pitch=args.pitch, fmt=args.fmt, seed=args.seed)
    with open(args.out, "wb") as f:
        f.write(audio)
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
```

---

## 4) `pyproject.toml` (sane defaults)

```toml
[project]
name = "tts-service"
version = "0.1.0"
description = "Site-agnostic TTS service (CLI + FastAPI) with pluggable providers"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.30.0",
  "pydantic>=2.7.0",
  "numpy>=1.26.0",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "mypy", "ruff", "black", "httpx", "requests"]

[project.scripts]
tts-gateway = "tts_gateway.cli:main"

[tool.ruff]
line-length = 100

[tool.black]
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true
```

---

## 5) Tests (examples)

### `tests/unit/test_providers_mock.py`

```python
from tts_service.providers.mock import MockProvider
import hashlib

def test_mock_is_deterministic():
    p = MockProvider()
    a = p.synthesize("Hello World", seed=123)
    b = p.synthesize("Hello World", seed=123)
    assert a == b
    md5 = hashlib.md5(a).hexdigest()
    assert len(a) > 1000
    assert isinstance(md5, str)
```

### `tests/integration/test_api_tts.py`

```python
from fastapi.testclient import TestClient
from tts_service.app import app

def test_api_tts_wav():
    c = TestClient(app)
    r = c.post("/api/v1/tts", json={"text":"Hello", "provider":"mock"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("audio/wav")
    assert len(r.content) > 1000
```

---

## 6) Docker & scripts

### `docker/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md /app/
RUN pip install --upgrade pip && pip install .
COPY src/ /app/src/
EXPOSE 8000
CMD ["uvicorn", "tts_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `docker/compose.yml`

```yaml
services:
  tts:
    build: ..
    ports:
      - "8000:8000"
```

### `scripts/dev.sh`

```bash
#!/usr/bin/env bash
uvicorn tts_gateway.app:app --reload
```

---

## 7) CI workflow

**`.github/workflows/ci.yml`**

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: |
          python -m pip install --upgrade pip
          pip install .[dev]
      - run: ruff check src tests
      - run: black --check src tests
      - run: mypy src
      - run: pytest -q
```

---

## 8) README outline

* One-liner + badges
* “Try it in 30s” (local + Docker)
* Quick API example (POST `/api/v1/tts`)
* CLI example (`tts --text "Hello" --out hello.wav`)
* Providers list (mock included; others optional)
* Legal note & contributions

---

## 9) Migration instructions from current tree

* [ ] Move `main.py` logic into `src/tts_service/app.py` and `api/v1/routes_tts.py`
* [ ] Move/rename tests: `poc_test.py`, `simple_test.py`, `test_service.py` → `tests/`
* [ ] Move sample texts to `examples/texts/`; drop large WAVs or keep tiny files in `examples/audio/`
* [ ] Replace `docker-compose.yml` with `docker/compose.yml`
* [ ] Replace `requirements.txt` with `pyproject.toml` (or generate requirements during Docker build)
* [ ] Add LEGAL, CONTRIBUTING, CODE_OF_CONDUCT; update README

---

## 10) Acceptance criteria (v0.1.0)

* `pytest` green locally and in GitHub Actions
* `ruff`, `black`, `mypy` pass
* `uvicorn tts_service.app:app` serves `/api/v1/tts` returning `audio/wav`
* `tts --text "Hello"` produces a WAV file
* Docker image builds and runs
* README clear enough for a first-time user to get sound in <2 minutes

---

