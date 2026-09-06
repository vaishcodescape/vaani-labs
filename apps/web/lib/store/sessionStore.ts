import { create } from "zustand";

import type { AnalysedToken, CodeSwitchSpan, PronunciationSource } from "@/lib/schemas/text";
import type { ServerEvent } from "@/lib/schemas/ws";

export type StreamStatus =
  | "idle"
  | "connecting"
  | "connected"
  | "analysing"
  | "running"
  | "paused"
  | "cancelled"
  | "completed"
  | "error";

export interface ChunkMetricRecord {
  sequence: number;
  acousticMs: number;
  vocoderMs: number;
  chunkLatencyMs: number;
  isFirstAudio: boolean;
}

export interface CompletionSummary {
  totalChunks: number;
  totalDurationMs: number;
  rtf: number;
  firstAudioLatencyMs: number;
  p50ChunkLatencyMs: number;
  p95ChunkLatencyMs: number;
  p99ChunkLatencyMs: number;
}

export interface StreamingControls {
  voiceId: string;
  speed: number;
  pitch: number;
  energy: number;
  streaming: boolean;
  chunkSizeMs: number;
  mrssSlowUpdateRate: number;
}

export const DEFAULT_CONTROLS: StreamingControls = {
  voiceId: "hi-female-1",
  speed: 1.0,
  pitch: 0.0,
  energy: 1.0,
  streaming: true,
  chunkSizeMs: 200,
  mrssSlowUpdateRate: 4,
};

interface WarningRecord {
  code: string;
  message: string;
}

export interface OfflineSynthesisResult {
  durationMs: number;
  rtf: number;
  sampleRate: number;
}

interface SessionState {
  sessionId: string | null;
  revisionId: number;
  status: StreamStatus;
  connectionOpen: boolean;
  sampleRate: number;

  text: string;
  tokens: AnalysedToken[];
  codeSwitchSpans: CodeSwitchSpan[];
  selectedTokenIndex: number | null;
  tokenDurationsMs: number[];

  controls: StreamingControls;

  chunkMetrics: ChunkMetricRecord[];
  bufferedMs: number;
  bufferUnderrun: boolean;
  waveformPeaks: number[];
  completion: CompletionSummary | null;
  warnings: WarningRecord[];
  errorMessage: string | null;
  lastPongAt: number | null;

  offlineLoading: boolean;
  offlineResult: OfflineSynthesisResult | null;
  setOfflineLoading: (loading: boolean) => void;
  setOfflineResult: (result: OfflineSynthesisResult | null) => void;

  setText: (text: string) => void;
  setAnalysisResult: (result: {
    text: string;
    tokens: AnalysedToken[];
    codeSwitchSpans: CodeSwitchSpan[];
  }) => void;
  setControls: (patch: Partial<StreamingControls>) => void;
  selectToken: (index: number | null) => void;
  updateTokenPronunciation: (
    index: number,
    phonemes: string,
    confidence: number,
    source: PronunciationSource,
  ) => void;

  setSessionId: (sessionId: string) => void;
  setConnectionOpen: (open: boolean) => void;
  applyServerEvent: (event: ServerEvent) => void;
  /** Returns true if the chunk belongs to the current revision and should be played. */
  acceptBinaryChunk: (revisionId: number, pcm: Int16Array) => boolean;
  setBufferStatus: (bufferedMs: number, underrun: boolean) => void;
  resetForNewSession: () => void;
}

const MAX_WAVEFORM_PEAKS = 600;

function peakOf(pcm: Int16Array): number {
  let max = 0;
  for (let i = 0; i < pcm.length; i++) {
    const abs = Math.abs(pcm[i] ?? 0);
    if (abs > max) max = abs;
  }
  return max / 32768;
}

export const useSessionStore = create<SessionState>((set, get) => ({
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
  setOfflineLoading: (loading) => set({ offlineLoading: loading }),
  setOfflineResult: (result) => set({ offlineResult: result }),

  setText: (text) => set({ text }),

  setAnalysisResult: ({ text, tokens, codeSwitchSpans }) =>
    set({ text, tokens, codeSwitchSpans, selectedTokenIndex: null }),

  setControls: (patch) => set((state) => ({ controls: { ...state.controls, ...patch } })),

  selectToken: (index) => set({ selectedTokenIndex: index }),

  updateTokenPronunciation: (index, phonemes, confidence, source) =>
    set((state) => ({
      tokens: state.tokens.map((token, i) =>
        i === index
          ? {
              ...token,
              pronunciation: { phonemes, confidence, is_uncertain: confidence < 0.7, source },
            }
          : token,
      ),
    })),

  setSessionId: (sessionId) => set({ sessionId }),

  setConnectionOpen: (open) => set({ connectionOpen: open, status: open ? "connected" : "idle" }),

  applyServerEvent: (event) =>
    set((state) => {
      switch (event.type) {
        case "session_started":
          return { revisionId: event.revision_id, status: "connected" as const };

        case "text_analysis":
          return {
            revisionId: event.revision_id,
            text: event.text,
            tokens: event.tokens,
            codeSwitchSpans: event.code_switch_spans,
            selectedTokenIndex: null,
            tokenDurationsMs: [],
            status: "analysing" as const,
            chunkMetrics: [],
            waveformPeaks: [],
            completion: null,
            bufferedMs: 0,
            bufferUnderrun: false,
          };

        case "synthesis_started":
          if (event.revision_id !== state.revisionId) return {};
          return {
            status: "running" as const,
            sampleRate: event.sample_rate,
            tokenDurationsMs: event.token_durations_ms,
          };

        case "audio_metadata":
          if (event.revision_id !== state.revisionId) return {};
          return { sampleRate: event.sample_rate };

        case "chunk_metric":
          if (event.revision_id !== state.revisionId) return {};
          return {
            chunkMetrics: [
              ...state.chunkMetrics,
              {
                sequence: event.sequence,
                acousticMs: event.acoustic_ms,
                vocoderMs: event.vocoder_ms,
                chunkLatencyMs: event.chunk_latency_ms,
                isFirstAudio: event.is_first_audio,
              },
            ],
          };

        case "buffer_status":
          if (event.revision_id !== state.revisionId) return {};
          return { bufferedMs: event.buffered_ms, bufferUnderrun: event.underflow };

        case "warning":
          return { warnings: [...state.warnings, { code: event.code, message: event.message }] };

        case "completed":
          if (event.revision_id !== state.revisionId) return {};
          return {
            status: "completed" as const,
            completion: {
              totalChunks: event.total_chunks,
              totalDurationMs: event.total_duration_ms,
              rtf: event.rtf,
              firstAudioLatencyMs: event.first_audio_latency_ms,
              p50ChunkLatencyMs: event.p50_chunk_latency_ms,
              p95ChunkLatencyMs: event.p95_chunk_latency_ms,
              p99ChunkLatencyMs: event.p99_chunk_latency_ms,
            },
          };

        case "cancelled":
          if (event.revision_id !== state.revisionId) return {};
          return { status: "cancelled" as const };

        case "error":
          return { status: "error" as const, errorMessage: event.message };

        case "pong":
          return { lastPongAt: Date.now() };

        default:
          return {};
      }
    }),

  acceptBinaryChunk: (revisionId, pcm) => {
    if (revisionId !== get().revisionId) return false;
    const peak = peakOf(pcm);
    set((state) => ({
      waveformPeaks:
        state.waveformPeaks.length >= MAX_WAVEFORM_PEAKS
          ? [...state.waveformPeaks.slice(1), peak]
          : [...state.waveformPeaks, peak],
    }));
    return true;
  },

  setBufferStatus: (bufferedMs, underrun) => set({ bufferedMs, bufferUnderrun: underrun }),

  resetForNewSession: () =>
    set({
      revisionId: 0,
      status: "idle",
      tokens: [],
      codeSwitchSpans: [],
      selectedTokenIndex: null,
      chunkMetrics: [],
      bufferedMs: 0,
      bufferUnderrun: false,
      waveformPeaks: [],
      completion: null,
      warnings: [],
      errorMessage: null,
    }),
}));
