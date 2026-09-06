/**
 * Binary WS chunk-frame parsing. Mirrors
 * packages/audio_metrics/audio_metrics/pcm.py's `pack_chunk_frame`:
 * a 12-byte big-endian header (revision_id, sequence, sample_count)
 * followed by little-endian PCM16 mono samples. See
 * docs/websocket-protocol.md "Binary chunk framing".
 */

const HEADER_SIZE = 12;

export interface ParsedChunkFrame {
  revisionId: number;
  sequence: number;
  pcm: Int16Array;
}

export function parseChunkFrame(buffer: ArrayBuffer): ParsedChunkFrame {
  const view = new DataView(buffer);
  const revisionId = view.getUint32(0, false);
  const sequence = view.getUint32(4, false);
  const sampleCount = view.getUint32(8, false);

  // Read explicitly as little-endian regardless of host byte order —
  // a plain `new Int16Array(buffer, HEADER_SIZE, sampleCount)` view
  // would silently assume native/host endianness instead.
  const pcm = new Int16Array(sampleCount);
  for (let i = 0; i < sampleCount; i++) {
    pcm[i] = view.getInt16(HEADER_SIZE + i * 2, true);
  }
  return { revisionId, sequence, pcm };
}
