# Architecture

## Overview

VaaniLab is a monorepo with a strict separation between the browser
frontend, the FastAPI backend, and three standalone Python packages that
hold all NLP/TTS *business logic*. The backend is a thin orchestration
layer: routers validate input, call services, services call injected
provider interfaces. No model-specific or NLP-specific logic lives in a
router, and no HTTP/WebSocket logic lives in a provider.

```
apps/web        Next.js (App Router, TS strict) — UI only, talks to the
                backend over REST + WebSocket via typed clients.
apps/api        FastAPI — routers + services + DI wiring + persistence.
                Depends on the three packages below; contains no
                linguistic or DSP logic itself.
packages/
  indic_text    Script/language/normalization/transliteration/G2P/
                pronunciation-ranking/lexicon interfaces + deterministic
                mock implementations. Pure Python, no FastAPI import.
  tts_runtime   Acoustic model + streaming vocoder interfaces, the mock
                implementations, and the stateful StreamingSynthesisSession
                engine (revisions, cancel/pause/resume, chunking).
  audio_metrics PCM fixture generation + AudioMetricCalculator (latency,
                RTF, percentile chunk latency). Used by tts_runtime and by
                API responses; has no dependency on FastAPI or the other
                two packages.
schemas/        JSON Schema documents, generated from the backend's
                Pydantic models via `scripts/export_schemas.py`, and
                consumed by the frontend's zod schemas as the source of
                truth for the wire contract. This directory is an
                addition beyond the originally requested structure —
                added because constraint #3 ("store shared JSON schemas
                where both systems can validate them") has no other home.
data/
  samples       Deterministic sample sentences (Hindi/Gujarati/Marathi/
                romanized/code-switched) used by the UI's sample picker
                and by backend fixtures/tests.
  lexicons      Seed SQLite/JSON lexicon data loaded on first run.
scripts/        Dev-environment helper scripts (seed DB, export schemas,
                run dev servers).
```

### Why this split

- **Testability.** `indic_text`, `tts_runtime`, and `audio_metrics` are
  pure Python with no web framework dependency, so their unit tests run
  in milliseconds and exercise real business logic instead of HTTP
  plumbing.
- **Swappability.** Every external model (LID, G2P, transliteration,
  acoustic model, vocoder) sits behind a `Protocol`/ABC defined once in
  the relevant package. Phase 2 replaces a mock class with a real one
  and changes exactly one line of dependency-injection wiring in
  `apps/api/app/deps.py`. See `model-adapter.md`.
- **Explicit contracts.** `docs/api-contract.md` and
  `docs/websocket-protocol.md` are the sources of truth for the wire
  format; both frontend (zod) and backend (Pydantic) validate against
  the same shapes, generated into `schemas/`.

## Dependency injection

`apps/api/app/deps.py` builds a single `ProviderRegistry` (a plain
dataclass of provider instances) at process startup from environment
configuration (`app/config.py`). FastAPI routes receive providers via
`Depends(get_registry)` — never import a concrete provider class
directly. Tests override `get_registry` to inject fakes/stubs distinct
from the "mock" providers (which are themselves the Phase-1
implementation, not test doubles).

## Streaming session as state machine

Every WebSocket connection to `/api/v1/synthesis/stream/{session_id}`
owns exactly one `StreamingSynthesisSession` (in `tts_runtime.session`).
States: `idle → running → (paused | cancelled | completed)`, with
`running` re-entered from `paused` on `resume` and re-entered from
itself (new revision) on `edit`. See `websocket-protocol.md` for the
full event/state table. Revision IDs are monotonically increasing
integers scoped to a session; the browser drops any binary chunk whose
header revision does not match the latest revision it has recorded.

## Data flow (streaming synthesis, happy path)

1. Browser `POST /api/v1/text/analyse` → tokens + pronunciation
   uncertainty flags (stateless, cacheable).
2. Browser optionally `POST /api/v1/pronunciation/candidates` /
   `.../preview` and `POST/PATCH /api/v1/lexicon` to correct
   pronunciations.
3. Browser opens `WS /api/v1/synthesis/stream/{session_id}` and sends a
   `start` event with text + controls.
4. Server re-analyses text (source of truth stays server-side), builds a
   `StreamingSynthesisSession`, emits `session_started`, `text_analysis`,
   `synthesis_started`, `audio_metadata`, then streams alternating
   `chunk_metric` (JSON) + binary PCM frames + periodic `buffer_status`
   until `completed`.
5. Browser's `AudioWorklet`-backed ring buffer consumes binary frames in
   sequence order and begins playback as soon as enough audio is
   buffered, independent of REST request/response timing.
6. `cancel` / `edit` / `pause` / `resume` mutate the session in place;
   `edit` increments the revision, and only chunks for the *unsynthesized*
   text region are regenerated.

## Persistence

SQLite (`data/lexicons/lexicon.db`, path from `.env`) via stdlib
`sqlite3` and a small repository class implementing the
`PronunciationLexicon` protocol from `indic_text`. No ORM: the schema is
one table and the access pattern is simple CRUD, so SQLAlchemy would add
weight without benefit (constraint #15's spirit — no infrastructure
ahead of measured need — applies here too).

## Frontend state

Zustand holds the single streaming-session slice: `sessionId`,
`revisionId`, connection status, tokens, chunk/metric history, buffer
health. REST calls (`analyse`, lexicon CRUD, `/models`, `/voices`,
`/languages`, `/system`) use React state local to their screens via a
thin typed fetch client in `lib/api/client.ts`; they do not go through
Zustand because they are not part of the streaming session's lifecycle.

## Testing strategy

- **Unit tests** for every provider's mock implementation and for
  `StreamingSynthesisSession` logic (revisions, cancellation, buffer
  underflow simulation) — `pytest`, no network/IO beyond in-memory
  SQLite.
- **API tests** using FastAPI's `TestClient`/`websockets` test harness
  for REST + WS contracts, including stale-chunk rejection and binary
  ordering.
- **Frontend unit tests** (Vitest + RTL) for token-chip interaction,
  pronunciation-candidate selection, and the ring-buffer/store logic.
- **E2E** (Playwright) for the primary workflow end-to-end against the
  real backend (mock providers), per constraint #20.

## Deferred infrastructure (explicitly out of scope until measured)

Redis, Celery/task queues, Kubernetes, horizontal autoscaling, GPU
scheduling, model registries. See `docs/model-adapter.md` for what
*does* need to change to add a real model, and the main task's "Phase 2"
list at the end of `README.md`.
