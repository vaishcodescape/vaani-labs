import { z } from "zod";

import { AnalysedTokenSchema, CodeSwitchSpanSchema } from "@/lib/schemas/text";

/**
 * Server -> client WS JSON event validation. Every text frame received
 * over the WebSocket is external input (constraint #14) and is parsed
 * through this discriminated union before the store or any component
 * touches it. See docs/websocket-protocol.md for the full event table.
 */

const SessionStartedSchema = z.object({
  type: z.literal("session_started"),
  session_id: z.string(),
  revision_id: z.number(),
});

const TextAnalysisSchema = z.object({
  type: z.literal("text_analysis"),
  session_id: z.string(),
  revision_id: z.number(),
  text: z.string(),
  tokens: z.array(AnalysedTokenSchema),
  code_switch_spans: z.array(CodeSwitchSpanSchema),
});

const SynthesisStartedSchema = z.object({
  type: z.literal("synthesis_started"),
  session_id: z.string(),
  revision_id: z.number(),
  sample_rate: z.number(),
  channels: z.number(),
  bit_depth: z.number(),
  estimated_duration_ms: z.number(),
  token_durations_ms: z.array(z.number()),
});

const AudioMetadataSchema = z.object({
  type: z.literal("audio_metadata"),
  session_id: z.string(),
  revision_id: z.number(),
  sample_rate: z.number(),
  channels: z.number(),
  bit_depth: z.number(),
  chunk_size_ms: z.number(),
});

const ChunkMetricSchema = z.object({
  type: z.literal("chunk_metric"),
  session_id: z.string(),
  revision_id: z.number(),
  sequence: z.number(),
  acoustic_ms: z.number(),
  vocoder_ms: z.number(),
  chunk_latency_ms: z.number(),
  is_first_audio: z.boolean(),
});

const BufferStatusSchema = z.object({
  type: z.literal("buffer_status"),
  session_id: z.string(),
  revision_id: z.number(),
  buffered_ms: z.number(),
  underflow: z.boolean(),
});

const WarningSchema = z.object({
  type: z.literal("warning"),
  code: z.string(),
  message: z.string(),
});

const CompletedSchema = z.object({
  type: z.literal("completed"),
  session_id: z.string(),
  revision_id: z.number(),
  total_chunks: z.number(),
  total_duration_ms: z.number(),
  rtf: z.number(),
  first_audio_latency_ms: z.number(),
  p50_chunk_latency_ms: z.number(),
  p95_chunk_latency_ms: z.number(),
  p99_chunk_latency_ms: z.number(),
});

const CancelledSchema = z.object({
  type: z.literal("cancelled"),
  session_id: z.string(),
  revision_id: z.number(),
});

const ErrorEventSchema = z.object({
  type: z.literal("error"),
  code: z.string(),
  message: z.string(),
});

const PongSchema = z.object({ type: z.literal("pong") });

export const ServerEventSchema = z.discriminatedUnion("type", [
  SessionStartedSchema,
  TextAnalysisSchema,
  SynthesisStartedSchema,
  AudioMetadataSchema,
  ChunkMetricSchema,
  BufferStatusSchema,
  WarningSchema,
  CompletedSchema,
  CancelledSchema,
  ErrorEventSchema,
  PongSchema,
]);
export type ServerEvent = z.infer<typeof ServerEventSchema>;

export interface StartClientEvent {
  type: "start";
  text: string;
  voice_id: string;
  speed: number;
  pitch: number;
  energy: number;
  streaming: boolean;
  chunk_size_ms: number;
  mrss_slow_update_rate: number;
}

export interface EditClientEvent {
  type: "edit";
  revision_id: number;
  unsynthesized_text: string;
  edit_offset_ms: number;
}

export type ClientEvent =
  | StartClientEvent
  | EditClientEvent
  | { type: "cancel" }
  | { type: "pause" }
  | { type: "resume" }
  | { type: "reset" }
  | { type: "ping" };
