# Mock → Real Model Integration Guide

This document is the Phase-2 entry point. It assumes you are a developer
(human or agent) replacing one or more mock providers with real models,
and touches **no** other part of the system.

## Golden rule

Every provider is a `typing.Protocol` (or ABC) defined in
`packages/indic_text/indic_text/interfaces.py` or
`packages/tts_runtime/tts_runtime/interfaces.py`. A real implementation:

1. Lives in its own module (e.g. `indic_text/real/indictrans_g2p.py` or
   a separate installable package if the model has heavy dependencies).
2. Implements the interface's methods with the exact same signature and
   return type.
3. Is wired in exactly one place: `apps/api/app/deps.py`
   (`build_provider_registry`), gated by an environment variable in
   `.env` (e.g. `G2P_PROVIDER=real-indictrans` vs `mock`).
4. Never imports FastAPI, and is never imported by a router directly.

No router, schema, WebSocket handler, or frontend code should need to
change when a mock is swapped for a real provider — if it does, the
interface boundary was drawn in the wrong place and should be fixed
first.

## Provider interfaces and their contracts

| Interface | Package | Method(s) | Contract |
|---|---|---|---|
| `ScriptDetector` | indic_text | `detect(text) -> list[ScriptSpan]` | Unicode-range based is fine even for "real"; rarely needs an ML model. |
| `LanguageIdentifier` | indic_text | `identify(text, script_hint) -> list[LanguageSpan]` | Must be deterministic for identical input; latency budget <10ms/token for interactive use. |
| `TextNormalizer` | indic_text | `normalize(token) -> NormalizedToken` | Must not change `token_type` classification contracts (number/date/abbreviation). |
| `CodeSwitchDetector` | indic_text | `detect(tokens) -> list[CodeSwitchSpan]` | Operates on already-tokenized, already-LID'd input. |
| `Transliterator` | indic_text | `transliterate(text, source_script, target_script) -> str` | Must be pure (no hidden state); used both for romanized-Indic normalization and lexicon lookups. |
| `GraphemeToPhoneme` | indic_text | `to_phonemes(token) -> list[PronunciationCandidate]` | Must return confidence in `[0,1]`; the ranker, not the G2P, decides `is_uncertain`. |
| `PronunciationRanker` | indic_text | `rank(candidates) -> list[PronunciationCandidate]` | Pure function over candidates; safe to swap independently of G2P. |
| `PronunciationLexicon` | indic_text | CRUD methods | Real deployments may replace SQLite with Postgres by implementing the same protocol — no API changes needed. |
| `AcousticModelAdapter` | tts_runtime | `plan(text, tokens, voice, controls) -> SynthesisPlan` | Must produce a duration estimate *before* vocoding starts, so `synthesis_started.estimated_duration_ms` stays meaningful. |
| `StreamingVocoderAdapter` | tts_runtime | `stream(plan) -> Iterator[AudioChunk]` | Must yield chunks in order, each with a wall-clock-plausible production delay if you want a real vocoder to be comparable to the RTF chart used for the mock, and must respect `chunk_size_ms` / MRSS slow-update-rate from the plan's controls. |
| `AudioMetricCalculator` | audio_metrics | `record_chunk(...)`, `summary()` | Provider-agnostic; you will not normally need to replace this one. |

## Integrating a real acoustic model

1. Implement `AcousticModelAdapter.plan()` to run your model's
   frontend/duration predictor and return a `SynthesisPlan` (defined in
   `tts_runtime/interfaces.py`) containing whatever internal
   representation your vocoder step needs (mel frames, latent codes,
   etc.) plus `estimated_duration_ms`.
2. Keep the call synchronous-per-chunk or async-generator based — the
   `StreamingSynthesisSession` in `tts_runtime/session.py` already
   handles cancellation/pause/revision bookkeeping around whatever the
   adapter yields; do not duplicate that logic in the adapter.
3. Add a unit test with a tiny fixture model (or a recorded
   input→output pair) mirroring the existing mock's test in
   `packages/tts_runtime/tests/test_acoustic_mock.py`.
4. Never commit model checkpoints (constraint #13). Load weights from a
   path in `.env` (`ACOUSTIC_MODEL_CHECKPOINT_PATH`) that is
   `.gitignore`d, or fetch from an artifact store at container start.

## Integrating MRSS-Vocos

1. Implement `StreamingVocoderAdapter.stream(plan)` as an
   (async) generator/iterator of `AudioChunk` (PCM16 mono int16 numpy
   array or bytes + `sample_rate`), respecting `plan.controls.chunk_size_ms`
   for chunk duration and `plan.controls.mrss_slow_update_rate` for how
   often MRSS's slow-path conditioning is recomputed vs. reused across
   chunks (mirror the mock's `SLOW_UPDATE_EVERY_N_CHUNKS` behavior in
   `tts_runtime/mock/vocoder.py` as the reference cadence contract).
2. Preserve chunk ordering and sequence numbering — the session assigns
   `sequence`/`revision_id` around whatever your adapter yields; do not
   reorder or buffer whole-utterance inside the adapter, or you defeat
   the point of streaming.
3. Benchmark real per-chunk latency and confirm `audio_metrics` P50/P95/P99
   numbers are computed correctly against the new timings (the
   calculator itself needs no changes).
4. Swap `.env`'s `VOCODER_PROVIDER=mock` → `VOCODER_PROVIDER=mrss-vocos`
   and update `deps.py`'s registry construction accordingly.

## Non-negotiables when integrating any real model

- Type-annotate every public function (constraint #16).
- Validate all external input before it reaches the model (constraint #17).
- Add a unit test for the new adapter's business logic (constraint #19).
- Never add authentication, Redis, Celery, or Kubernetes as a side
  effect of "just getting the model to run faster" — profile first,
  raise the requirement explicitly, then revisit constraint #15.
