import { z } from "zod";

export const OfflineSynthesisRequestSchema = z.object({
  text: z.string(),
  voice_id: z.string(),
  speed: z.number().min(0.5).max(2.0).default(1.0),
  pitch: z.number().min(-12).max(12).default(0.0),
  energy: z.number().min(0.25).max(2.0).default(1.0),
});
export type OfflineSynthesisRequest = z.infer<typeof OfflineSynthesisRequestSchema>;

export const OfflineSynthesisResponseSchema = z.object({
  sample_rate: z.number(),
  channels: z.number(),
  bit_depth: z.number(),
  duration_ms: z.number(),
  rtf: z.number(),
  pcm_base64: z.string(),
});
export type OfflineSynthesisResponse = z.infer<typeof OfflineSynthesisResponseSchema>;
