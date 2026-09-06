import { z } from "zod";

export const LexiconEntrySchema = z.object({
  id: z.string(),
  surface: z.string(),
  language: z.string(),
  phonemes: z.string(),
  notes: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type LexiconEntry = z.infer<typeof LexiconEntrySchema>;

export const LexiconListResponseSchema = z.object({
  entries: z.array(LexiconEntrySchema),
});
export type LexiconListResponse = z.infer<typeof LexiconListResponseSchema>;

export const LexiconCreateRequestSchema = z.object({
  surface: z.string().min(1),
  language: z.string().min(1),
  phonemes: z.string().min(1),
  notes: z.string().default(""),
});
export type LexiconCreateRequest = z.infer<typeof LexiconCreateRequestSchema>;

export const LexiconUpdateRequestSchema = z.object({
  phonemes: z.string().optional(),
  notes: z.string().optional(),
});
export type LexiconUpdateRequest = z.infer<typeof LexiconUpdateRequestSchema>;
