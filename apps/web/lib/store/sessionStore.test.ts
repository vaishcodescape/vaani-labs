import { beforeEach, describe, expect, it } from "vitest";

import { DEFAULT_CONTROLS, useSessionStore } from "@/lib/store/sessionStore";
import type { AnalysedToken } from "@/lib/schemas/text";

const sampleToken: AnalysedToken = {
  index: 0,
  surface: "meeting",
  start_offset: 0,
  end_offset: 7,
  script: "Latin",
  language: "en",
  normalized: "meeting",
  token_type: "word",
  codepoints: [],
  pronunciation: { phonemes: "m iː t ɪ ŋ", confidence: 0.5, is_uncertain: true, source: "g2p" },
};

beforeEach(() => {
  useSessionStore.setState({
    sessionId: null,
    revisionId: 0,
    status: "idle",
    connectionOpen: false,
    sampleRate: 22050,
    text: "",
    tokens: [],
    codeSwitchSpans: [],
    selectedTokenIndex: null,
    tokenDurationsMs: [],
    controls: DEFAULT_CONTROLS,
    chunkMetrics: [],
    bufferedMs: 0,
    bufferUnderrun: false,
    waveformPeaks: [],
    completion: null,
    warnings: [],
    errorMessage: null,
    lastPongAt: null,
    offlineLoading: false,
    offlineResult: null,
  });
});

describe("sessionStore token selection", () => {
  it("selects and deselects a token by index", () => {
    useSessionStore.setState({ tokens: [sampleToken] });
    useSessionStore.getState().selectToken(0);
    expect(useSessionStore.getState().selectedTokenIndex).toBe(0);
    useSessionStore.getState().selectToken(null);
    expect(useSessionStore.getState().selectedTokenIndex).toBeNull();
  });

  it("updates a token's pronunciation candidate selection", () => {
    useSessionStore.setState({ tokens: [sampleToken] });
    useSessionStore.getState().updateTokenPronunciation(0, "m iː ʈ ɪ ŋ", 0.9, "g2p-alt");
    const token = useSessionStore.getState().tokens[0];
    expect(token?.pronunciation.phonemes).toBe("m iː ʈ ɪ ŋ");
    expect(token?.pronunciation.confidence).toBe(0.9);
    expect(token?.pronunciation.is_uncertain).toBe(false);
    expect(token?.pronunciation.source).toBe("g2p-alt");
  });
});

describe("sessionStore revision handling", () => {
  it("accepts a binary chunk for the current revision and rejects a stale one", () => {
    useSessionStore.setState({ revisionId: 2 });
    const pcm = new Int16Array([1000, -1000]);
    expect(useSessionStore.getState().acceptBinaryChunk(2, pcm)).toBe(true);
    expect(useSessionStore.getState().acceptBinaryChunk(1, pcm)).toBe(false);
    // Only the accepted chunk should have contributed a waveform peak.
    expect(useSessionStore.getState().waveformPeaks.length).toBe(1);
  });

  it("ignores chunk_metric events for a revision that is no longer current", () => {
    useSessionStore.setState({ revisionId: 2 });
    useSessionStore.getState().applyServerEvent({
      type: "chunk_metric",
      session_id: "s1",
      revision_id: 1,
      sequence: 0,
      acoustic_ms: 5,
      vocoder_ms: 5,
      chunk_latency_ms: 10,
      is_first_audio: true,
    });
    expect(useSessionStore.getState().chunkMetrics).toHaveLength(0);
  });

  it("applies chunk_metric events for the current revision", () => {
    useSessionStore.setState({ revisionId: 1 });
    useSessionStore.getState().applyServerEvent({
      type: "chunk_metric",
      session_id: "s1",
      revision_id: 1,
      sequence: 0,
      acoustic_ms: 5,
      vocoder_ms: 5,
      chunk_latency_ms: 10,
      is_first_audio: true,
    });
    expect(useSessionStore.getState().chunkMetrics).toHaveLength(1);
  });

  it("bumps the current revision on text_analysis and clears per-revision state", () => {
    useSessionStore.setState({
      revisionId: 1,
      chunkMetrics: [
        { sequence: 0, acousticMs: 1, vocoderMs: 1, chunkLatencyMs: 2, isFirstAudio: true },
      ],
    });
    useSessionStore.getState().applyServerEvent({
      type: "text_analysis",
      session_id: "s1",
      revision_id: 2,
      text: "दुनिया",
      tokens: [],
      code_switch_spans: [],
    });
    const state = useSessionStore.getState();
    expect(state.revisionId).toBe(2);
    expect(state.chunkMetrics).toHaveLength(0);
    expect(state.status).toBe("analysing");
  });

  it("records a completion summary only for the current revision", () => {
    useSessionStore.setState({ revisionId: 3 });
    useSessionStore.getState().applyServerEvent({
      type: "completed",
      session_id: "s1",
      revision_id: 2,
      total_chunks: 5,
      total_duration_ms: 500,
      rtf: 0.1,
      first_audio_latency_ms: 20,
      p50_chunk_latency_ms: 10,
      p95_chunk_latency_ms: 15,
      p99_chunk_latency_ms: 20,
    });
    expect(useSessionStore.getState().completion).toBeNull();

    useSessionStore.getState().applyServerEvent({
      type: "completed",
      session_id: "s1",
      revision_id: 3,
      total_chunks: 5,
      total_duration_ms: 500,
      rtf: 0.1,
      first_audio_latency_ms: 20,
      p50_chunk_latency_ms: 10,
      p95_chunk_latency_ms: 15,
      p99_chunk_latency_ms: 20,
    });
    expect(useSessionStore.getState().completion?.totalChunks).toBe(5);
    expect(useSessionStore.getState().status).toBe("completed");
  });
});
