# WebSocket Streaming Protocol — v1

Endpoint: `WS /api/v1/synthesis/stream/{session_id}`

`session_id` is generated client-side (UUID v4) before opening the
connection and is the stable identity of one Synthesis Studio "run"
across `start` → `edit`* → `completed`/`cancelled`. Opening a connection
does not itself start synthesis; the client must send a `start` event.

Two frame kinds travel over the one socket:

- **Text frames**: JSON, one object per frame, always `{"type": "...", ...}`.
- **Binary frames**: exactly one audio chunk each, see "Binary chunk
  framing" below. Never JSON, never base64 (constraint #12).

All JSON events that relate to an in-flight synthesis carry
`session_id` and `revision_id` so the client can ignore anything that
does not match its current revision, mirroring the binary header check.

## Revisions

`revision_id` starts at `1` on `start` and increments by 1 on every
`edit`. A revision is scoped to a `session_id`. The server never reuses
a lower revision number and never emits chunks for a revision below the
current one after processing an `edit`. The client tracks
`latestRevisionId` and discards (does not decode, does not buffer,
does not count toward metrics) any binary frame or chunk-scoped JSON
event whose `revision_id` is less than `latestRevisionId`.

## Client → Server events

| type      | payload fields                                                                 | effect |
|-----------|---------------------------------------------------------------------------------|--------|
| `start`   | `text, voice_id, speed, pitch, energy, streaming, chunk_size_ms, mrss_slow_update_rate` | Begins revision 1. Server re-runs `/text/analyse` server-side (never trusts client-derived tokens) and starts producing chunks. |
| `edit`    | `revision_id` (client's proposed next id — server validates it is `current+1`), `unsynthesized_text`, `edit_offset_ms` | Server discards any in-flight generation beyond `edit_offset_ms` of already-produced audio, starts a new revision synthesizing `unsynthesized_text` onward, and continues streaming under the new `revision_id`. Audio already sent for the prior revision up to `edit_offset_ms` is kept by the client — not resent. |
| `cancel`  | — | Stops generation for the current revision immediately; server replies `cancelled`, connection stays open (idle) unless client closes it. |
| `pause`   | — | Suspends chunk emission; session stays `running`→`paused`, no new chunks until `resume`. |
| `resume`  | — | Resumes chunk emission for the current revision from where it paused. |
| `reset`   | — | Returns the session to `idle`, revision counter resets to 0, ready for a new `start`. |
| `ping`    | — | Server replies `pong` immediately; used for connection-health checks, not a keepalive requirement (the server does not time out idle connections in Phase 1). |

## Server → Client events (JSON text frames)

| type               | payload fields | when |
|--------------------|-----------------|------|
| `session_started`  | `session_id, revision_id` | immediately after a valid `start` |
| `text_analysis`    | `session_id, revision_id, tokens[]` (same shape as `POST /text/analyse`) | right after `session_started`, before audio begins |
| `synthesis_started`| `session_id, revision_id, sample_rate, channels, bit_depth, estimated_duration_ms, token_durations_ms[]` | once acoustic-model "planning" completes. `token_durations_ms` aligns 1:1 with the `tokens[]` from the preceding `text_analysis` event and drives the token-alignment timeline. |
| `audio_metadata`   | `session_id, revision_id, sample_rate, channels, bit_depth, chunk_size_ms` | once per revision, before the first binary frame of that revision |
| `chunk_metric`     | `session_id, revision_id, sequence, acoustic_ms, vocoder_ms, chunk_latency_ms, is_first_audio` | once per chunk, immediately before that chunk's binary frame |
| `buffer_status`    | `session_id, revision_id, buffered_ms, underflow` | periodically (every chunk) so the client can cross-check its own ring-buffer estimate against the server's production rate |
| `warning`          | `code, message` | non-fatal issue, e.g. simulated buffer underflow |
| `completed`        | `session_id, revision_id, total_chunks, total_duration_ms, rtf, first_audio_latency_ms, p50_chunk_latency_ms, p95_chunk_latency_ms, p99_chunk_latency_ms` | after the last chunk of a revision that was not interrupted |
| `cancelled`        | `session_id, revision_id` | after a `cancel` is processed |
| `error`            | `code, message` | malformed client event, invalid revision transition, internal error |
| `pong`             | — | reply to `ping` |

## Binary chunk framing

Each audio chunk is **one binary WebSocket frame**:

```
byte offset  size  field          type
0            4     revision_id    uint32 big-endian
4            4     sequence       uint32 big-endian
8            4     sample_count   uint32 big-endian
12           N*2   pcm            int16 little-endian, mono, N = sample_count
```

Rationale for a binary header instead of a paired JSON+binary message
pair: WebSocket guarantees frame ordering on a single connection, so a
self-describing binary frame lets the client validate and route a chunk
without relying on message interleaving order between two independent
frames. The preceding `chunk_metric` JSON event (same `sequence` +
`revision_id`) carries timing metadata that doesn't need to be
re-sent per chunk in the binary frame itself.

`sample_count * 2` bytes of PCM16LE follow the header immediately; the
frame contains nothing else. Sample rate/channels/bit-depth are fixed
for the lifetime of a revision and announced once via `audio_metadata`.

## Client-side stale-chunk handling

```ts
function onBinaryFrame(buf: ArrayBuffer) {
  const view = new DataView(buf);
  const revisionId = view.getUint32(0, false);
  const sequence = view.getUint32(4, false);
  const sampleCount = view.getUint32(8, false);
  if (revisionId < store.latestRevisionId) return; // discard stale
  const pcm = new Int16Array(buf, 12, sampleCount);
  ringBuffer.push(revisionId, sequence, pcm);
}
```

## State machine

```
idle --start--> running --cancel--> cancelled --reset--> idle
running --pause--> paused --resume--> running
running --edit--> running (revision+1)
running --(last chunk sent)--> completed --reset--> idle
any state --error (fatal)--> idle (connection remains open)
```

## Simulated buffer underflow (Phase 1 test hook)

To exercise `buffer_status.underflow` and the frontend's underflow UI
without needing real load, the mock engine deterministically triggers
one underflow event when the *first* streaming session's chunk index
reaches `3` (see `tts_runtime.session.UNDERFLOW_TEST_CHUNK_INDEX`). It
emits `warning {code: "SIMULATED_BUFFER_UNDERFLOW"}` and a
`buffer_status {underflow: true}` before continuing normally. This is
documented here because it is deliberate, reproducible test behavior,
not a bug.
