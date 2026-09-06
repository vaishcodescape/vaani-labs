import { z } from "zod";

import { PronunciationSourceSchema } from "@/lib/schemas/text";

export const PronunciationCandidateSchema = z.object({
  phonemes: z.string(),
  confidence: z.number(),
  source: PronunciationSourceSchema,
});
export type PronunciationCandidate = z.infer<typeof PronunciationCandidateSchema>;

export const PronunciationCandidatesResponseSchema = z.object({
  surface: z.string(),
  candidates: z.array(PronunciationCandidateSchema),
});
export type PronunciationCandidatesResponse = z.infer<typeof PronunciationCandidatesResponseSchema>;

export const PronunciationPreviewResponseSchema = z.object({
  sample_rate: z.number(),
  channels: z.number(),
  bit_depth: z.number(),
  pcm_base64: z.string(),
});
export type PronunciationPreviewResponse = z.infer<typeof PronunciationPreviewResponseSchema>;
