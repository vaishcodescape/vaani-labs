# REST API Contract — v1

Base path: `/api/v1`. All bodies are JSON. All errors use the structured
error envelope (see below). This document is the source of truth; the
Pydantic models in `apps/api/app/schemas/` and the exported JSON Schemas
in `schemas/` must match it.

## Structured error envelope

Every non-2xx response body:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "text must not be empty",
    "details": { "field": "text" }
  }
}
```

`code` is a stable machine-readable string (`VALIDATION_ERROR`,
`NOT_FOUND`, `INVALID_UTF8`, `TEXT_TOO_LONG`, `SESSION_NOT_FOUND`,
`INTERNAL_ERROR`). `details` is optional and free-form.

## GET /api/v1/health

Liveness probe. No auth, no dependencies exercised.

Response `200`:
```json
{ "status": "ok", "version": "0.1.0" }
```

## GET /api/v1/system

Aggregate system info for the **System Status** screen.

Response `200`:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptime_seconds": 1234.5,
  "providers": {
    "script_detector": "mock-unicode-range",
    "language_identifier": "mock-heuristic-lid",
    "normalizer": "mock-rule-normalizer",
    "code_switch_detector": "mock-heuristic-csd",
    "transliterator": "mock-charmap-transliterator",
    "g2p": "mock-rule-g2p",
    "pronunciation_ranker": "mock-confidence-ranker",
    "lexicon": "sqlite-lexicon",
    "acoustic_model": "mock-duration-acoustic",
    "vocoder": "mock-sine-mrss-vocos",
    "audio_metrics": "in-process-audio-metrics"
  },
  "active_sessions": 0,
  "lexicon_entry_count": 12
}
```

## GET /api/v1/models

Response `200`: list of model adapters and whether they are mock or real.
```json
{
  "acoustic_models": [{ "id": "mock-duration-acoustic", "kind": "mock", "is_default": true }],
  "vocoders": [{ "id": "mock-sine-mrss-vocos", "kind": "mock", "is_default": true }]
}
```

## GET /api/v1/voices

Response `200`:
```json
{
  "voices": [
    { "id": "hi-female-1", "language": "hi", "label": "Hindi — Female 1", "gender": "female" },
    { "id": "hi-male-1", "language": "hi", "label": "Hindi — Male 1", "gender": "male" },
    { "id": "gu-female-1", "language": "gu", "label": "Gujarati — Female 1", "gender": "female" },
    { "id": "mr-female-1", "language": "mr", "label": "Marathi — Female 1", "gender": "female" }
  ]
}
```

## GET /api/v1/languages

Response `200`:
```json
{
  "languages": [
    { "code": "hi", "name": "Hindi", "script": "Devanagari" },
    { "code": "gu", "name": "Gujarati", "script": "Gujarati" },
    { "code": "mr", "name": "Marathi", "script": "Devanagari" },
    { "code": "en", "name": "English", "script": "Latin" }
  ]
}
```

## POST /api/v1/text/analyse

Request:
```json
{ "text": "मुझे कल 5 बजे meeting है।" }
```
Constraints: `text` is 1..=5000 Unicode codepoints (post NFC), must be
valid Unicode (surrogate/invalid sequences rejected with
`INVALID_UTF8`). Empty string → `VALIDATION_ERROR`.

Response `200`:
```json
{
  "text": "मुझे कल 5 बजे meeting है।",
  "tokens": [
    {
      "index": 0,
      "surface": "मुझे",
      "start_offset": 0,
      "end_offset": 4,
      "script": "Devanagari",
      "language": "hi",
      "normalized": "मुझे",
      "token_type": "word",
      "codepoints": ["U+092E", "U+0941", "U+091D", "U+0947"],
      "pronunciation": {
        "phonemes": "m ʊ dʒ ʱ eː",
        "confidence": 0.94,
        "is_uncertain": false,
        "source": "g2p"
      }
    },
    {
      "index": 4,
      "surface": "meeting",
      "start_offset": 13,
      "end_offset": 20,
      "script": "Latin",
      "language": "en",
      "normalized": "meeting",
      "token_type": "word",
      "codepoints": ["U+006D", "..."],
      "pronunciation": {
        "phonemes": "m iː t ɪ ŋ",
        "confidence": 0.55,
        "is_uncertain": true,
        "source": "g2p"
      }
    }
  ],
  "code_switch_spans": [{ "start_offset": 13, "end_offset": 20, "language": "en" }]
}
```
`token_type` ∈ `word | number | date | abbreviation | punctuation |
whitespace`. `pronunciation.source` ∈ `lexicon | g2p`. A token whose
surface form matches a lexicon entry always has `source: "lexicon"` and
`is_uncertain: false`.

## POST /api/v1/text/normalize

Request: `{ "text": "5" }` → Response `200`:
```json
{ "text": "5", "normalized": "पाँच", "token_type": "number" }
```
Used standalone (e.g. hovering a token) as well as internally by
`/text/analyse`.

## POST /api/v1/pronunciation/candidates

Request:
```json
{ "surface": "meeting", "language": "en", "script": "Latin" }
```
Response `200`:
```json
{
  "surface": "meeting",
  "candidates": [
    { "phonemes": "m iː t ɪ ŋ", "confidence": 0.55, "source": "g2p" },
    { "phonemes": "m iː ʈ ɪ ŋ", "confidence": 0.31, "source": "g2p-alt" },
    { "phonemes": "m iː t i ŋ ɡ", "confidence": 0.12, "source": "g2p-alt" }
  ]
}
```
Candidates are always sorted descending by `confidence`. Mock ranker
generates 1–3 deterministic candidates per surface form.

## POST /api/v1/pronunciation/preview

Request: `{ "surface": "meeting", "phonemes": "m iː t ɪ ŋ", "voice_id": "hi-female-1" }`
Response `200`: a short offline-synthesized WAV of just that token.
```json
{ "sample_rate": 22050, "channels": 1, "bit_depth": 16, "pcm_base64": "..." }
```
This is the **one** endpoint permitted to base64-encode PCM: it is a
small (<1s) preview fetched over plain JSON/REST, not the streaming
path, so constraint #12 (no base64 for streamed PCM) does not apply.

## GET /api/v1/lexicon

Query params: `q` (optional substring filter), `language` (optional).
Response `200`:
```json
{
  "entries": [
    {
      "id": "a1b2c3",
      "surface": "meeting",
      "language": "en",
      "phonemes": "m iː t ɪ ŋ",
      "notes": "corrected during 2026-09 demo prep",
      "created_at": "2026-09-01T10:00:00Z",
      "updated_at": "2026-09-01T10:00:00Z"
    }
  ]
}
```

## POST /api/v1/lexicon

Request: `{ "surface": "meeting", "language": "en", "phonemes": "m iː t ɪ ŋ", "notes": "" }`
Response `201`: the created entry (shape above). `surface+language` is
unique; conflicting insert → `409` with code `LEXICON_CONFLICT`.

## PATCH /api/v1/lexicon/{entry_id}

Request: any subset of `{ "phonemes": "...", "notes": "..." }`.
Response `200`: updated entry. Unknown `entry_id` → `404 NOT_FOUND`.

## DELETE /api/v1/lexicon/{entry_id}

Response `204`. Unknown `entry_id` → `404 NOT_FOUND`.

## POST /api/v1/synthesis/offline

Request:
```json
{
  "text": "...",
  "voice_id": "hi-female-1",
  "speed": 1.0,
  "pitch": 0.0,
  "energy": 1.0
}
```
`speed` ∈ [0.5, 2.0], `pitch` ∈ [-12, 12] semitones, `energy` ∈ [0.25, 2.0].
Response `200`:
```json
{
  "sample_rate": 22050,
  "channels": 1,
  "bit_depth": 16,
  "duration_ms": 2340,
  "rtf": 0.08,
  "pcm_base64": "..."
}
```
Offline synthesis returns the *entire* utterance in one response, so
base64 is acceptable here (constraint #12 applies to the streaming path).

## WS /api/v1/synthesis/stream/{session_id}

See `docs/websocket-protocol.md`.
