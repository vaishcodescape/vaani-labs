# Product Requirements — VaaniLab

## Product goals

VaaniLab is a demo-quality, research-grade web platform for interactive Indic
text-to-speech (TTS). It exists to let researchers and conference audiences:

1. Type or paste Hindi, Gujarati, Marathi, romanized Indic, or Indic-English
   code-switched text and see exactly how the system understands it token by
   token (script, language, normalized form, pronunciation).
2. See which pronunciations the system is *uncertain* about, compare
   alternative pronunciation candidates, and correct them by hand.
3. Persist corrections into a reusable pronunciation lexicon so the same
   mistake is never corrected twice.
4. Control voice, prosody (speed/pitch/energy) and streaming behavior
   (chunk size, MRSS slow-update-rate) and hear the effect immediately.
5. Watch audio start playing before synthesis finishes, via chunked
   streaming over a WebSocket into a browser-side ring buffer.
6. Observe the operational characteristics of streaming synthesis:
   first-audio latency, real-time factor (RTF), and chunk-latency
   percentiles — not just the audio itself.
7. Edit the *unsynthesized* remainder of the text mid-stream and resume
   without re-playing or re-generating audio that has already been
   produced and heard.
8. Compare the streaming path against a one-shot offline synthesis call.

## Non-goals (for this repository, at this stage)

- **No real acoustic model or vocoder.** Phase 1 ships a fully mocked
  pipeline behind the exact interfaces the real models will implement.
  Model integration is explicitly deferred (see `model-adapter.md`).
- **No authentication or multi-tenant access control.** This is a
  single-user conference/demo tool, not a hosted product.
- **No distributed serving.** No Redis, Celery, message queues, or
  Kubernetes — a single FastAPI process and a single SQLite file are
  sufficient until a measured requirement says otherwise.
- **No production-grade lexicon governance** (versioning, review
  workflows, multi-user conflict resolution). The lexicon is a flat,
  correctable key/value store.
- **No mobile-optimized layout.** The UI targets a 1440×900 desktop/demo
  resolution; responsive/mobile layout is out of scope.
- **No linguistic completeness claims.** Mock language ID, G2P and
  transliteration are heuristic and intentionally simplistic — they exist
  to exercise the interfaces and UI, not to be linguistically correct.

## Primary user workflow (what "done" means)

1. User opens **Synthesis Studio**, picks or types a mixed-language
   sentence.
2. User clicks **Analyse Text** → token chips render with script/language
   labels; low-confidence pronunciation tokens are visually flagged.
3. User clicks a flagged token → pronunciation candidate panel opens,
   shows ranked candidates with confidence, user picks one or hand-edits
   the phoneme string.
4. User saves the correction to the lexicon (persists to SQLite, visible
   in **Pronunciation Lexicon** screen).
5. User sets speaker/speed/pitch/energy/streaming controls and clicks
   **Start**. Audio begins playing before the full utterance is
   synthesized; waveform, token-alignment timeline and latency metrics
   update live.
6. User clicks **Cancel** mid-stream → playback and generation stop
   immediately.
7. User edits the *unsynthesized* tail of the text and clicks **Resume**
   → synthesis continues from the edit point under a new revision;
   already-played audio is not replayed or regenerated.
8. User compares the same text synthesized via **offline** mode.

## Target users

- TTS/NLP researchers iterating on pronunciation correctness for Indic
  languages.
- Conference demo presenters who need a robust, readable, fast UI at
  1440×900.
- Downstream engineers (including future coding agents) who will replace
  the mock providers with real models without touching UI or protocol
  code.
