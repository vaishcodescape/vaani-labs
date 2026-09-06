# VaaniLab

**An Interactive Platform for Pronunciation-Aware, Controllable, and
Streaming Indic Text-to-Speech.**

VaaniLab is a conference-demo-quality web application for interactive
Hindi/Gujarati/Marathi/romanized-Indic/code-switched text-to-speech: it
shows exactly how the system reads a sentence (script, language,
pronunciation, uncertainty), lets you correct pronunciations into a
reusable lexicon, and streams generated audio into the browser chunk by
chunk with live latency metrics.

**Phase 1 status: complete, mock-only.** Every NLP/TTS provider
(language ID, normalization, transliteration, G2P, acoustic model,
vocoder) is a deterministic mock behind the exact interface a real
model will later implement — see `docs/model-adapter.md`. No real
model is integrated yet; that is intentional (see "Current
limitations" below).

## Repository layout

```
apps/web        Next.js (App Router, TS strict) frontend
apps/api        FastAPI backend (REST + WebSocket)
packages/
  indic_text    Script/LID/normalization/transliteration/G2P/lexicon
  tts_runtime   Acoustic model + vocoder interfaces, mocks, streaming session
  audio_metrics PCM fixtures, WS binary framing, latency/RTF metrics
schemas/        JSON Schema exported from the API's Pydantic models
data/
  samples       Deterministic sample sentences
  lexicons      SQLite lexicon data (gitignored; created on first run)
scripts/        Dev helper scripts (seed lexicon, export schemas)
docs/           Product/architecture/API/WS/model-adapter/demo docs
```

See `docs/architecture.md` for why it's shaped this way, and
`AGENTS.md` for the engineering rules that govern this repository.

## Prerequisites

- Python 3.12+ (backend targets 3.12; developed against 3.13/3.14 —
  Docker images pin `python:3.12-slim`)
- Node.js 20+ and npm
- Docker + Docker Compose (optional, for the containerized path)

## Quick start (local, no Docker)

```bash
make install        # creates .venv, installs backend packages + frontend deps
make seed            # optional: seed a couple of demo lexicon corrections
make dev-backend     # terminal 1 — FastAPI on :8000
make dev-frontend    # terminal 2 — Next.js on :3000
```

Then open <http://localhost:3000> (redirects to `/studio`).

## Quick start (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

Frontend: <http://localhost:3000>. Backend: <http://localhost:8000>.

## Running tests

```bash
make test              # backend (4 packages) + frontend unit tests
make test-backend      # pytest for indic_text, audio_metrics, tts_runtime, api
make test-frontend     # vitest + React Testing Library
make e2e                # Playwright — requires the backend running on :8000
```

## Linting and type checking

```bash
make lint               # ruff (backend) + eslint (frontend)
make typecheck           # mypy --strict (backend) + tsc --noEmit (frontend)
```

## Running the conference demo

See `docs/demo-script.md` for a scripted ~6-minute walkthrough of the
primary workflow (analyse → correct pronunciation → stream → cancel →
edit-and-resume → compare offline).

## Documentation index

| Doc | Contents |
|---|---|
| `docs/product-requirements.md` | Goals, non-goals, primary user workflow |
| `docs/architecture.md` | System shape, data flow, why it's structured this way |
| `docs/api-contract.md` | Every REST endpoint, request/response shapes, error envelope |
| `docs/websocket-protocol.md` | WS event tables, binary frame format, revision/state machine |
| `docs/model-adapter.md` | Exactly how to replace a mock provider with a real model |
| `docs/demo-script.md` | Scripted conference walkthrough |

## Current limitations (Phase 1)

- **All NLP/TTS providers are deterministic mocks.** Script detection is
  real (Unicode-range based); language ID, normalization,
  transliteration, and G2P are heuristic/rule-based, not ML models;
  the "acoustic model" estimates duration from phoneme counts; the
  vocoder ("MRSS-Vocos" stand-in) generates per-token sine tones. See
  `docs/model-adapter.md` for the swap-in procedure.
- **Mid-stream edit is a Phase-1 simplification.** The UI lets you edit
  the whole visible text and resume as a new revision; it does not yet
  lock/gray out a precise "already spoken" character prefix computed
  from live playback position — see `components/studio/EditResumeBar.tsx`
  and `docs/demo-script.md`.
- **Offline synthesis RTF is near-zero.** The mock vocoder does no real
  DSP work, so the offline endpoint's measured real-time factor
  reflects mock overhead, not a claim about a real model's performance.
- **No authentication, no multi-user isolation, no Redis/Celery/K8s** —
  deliberately out of scope until a measured requirement exists
  (constraints #14–#15 in the original task brief).
- **Frontend dependency audit:** `next`'s vendored internal `postcss`
  carries known advisories only fixed by a Next.js 16 major upgrade;
  deferred to Phase 2 to avoid an unreviewed major-version jump this
  late in a demo build. Not otherwise reachable at runtime for a
  locally-run demo tool. Run `npm audit` in `apps/web` to review.
- **Local dev Python version:** the sandbox this was built in only had
  Python 3.13/3.14 available; packages declare `>=3.12` and Docker
  images pin `python:3.12-slim`, but CI/local dev on exactly 3.12
  hasn't been separately verified here.

## Phase 2 (deferred)

See the end of this file's originating task brief / `docs/model-adapter.md`
for the exact procedure. In short: implement one real provider at a
time behind its existing interface, wire it in `apps/api/app/deps.py`
behind an env var, and never change a router, schema, or frontend
component to do it.
