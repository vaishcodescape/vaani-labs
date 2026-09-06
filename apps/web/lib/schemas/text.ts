import { z } from "zod";

export const TokenTypeSchema = z.enum([
  "word",
  "number",
  "date",
  "abbreviation",
  "punctuation",
  "whitespace",
]);
export type TokenType = z.infer<typeof TokenTypeSchema>;

export const PronunciationSourceSchema = z.enum(["lexicon", "g2p", "g2p-alt"]);
export type PronunciationSource = z.infer<typeof PronunciationSourceSchema>;

export const TokenPronunciationSchema = z.object({
  phonemes: z.string(),
  confidence: z.number(),
  is_uncertain: z.boolean(),
  source: PronunciationSourceSchema,
});
export type TokenPronunciation = z.infer<typeof TokenPronunciationSchema>;

export const AnalysedTokenSchema = z.object({
  index: z.number(),
  surface: z.string(),
  start_offset: z.number(),
  end_offset: z.number(),
  script: z.string(),
  language: z.string(),
  normalized: z.string(),
  token_type: TokenTypeSchema,
  codepoints: z.array(z.string()),
  pronunciation: TokenPronunciationSchema,
});
export type AnalysedToken = z.infer<typeof AnalysedTokenSchema>;

export const CodeSwitchSpanSchema = z.object({
  start_offset: z.number(),
  end_offset: z.number(),
  language: z.string(),
});
export type CodeSwitchSpan = z.infer<typeof CodeSwitchSpanSchema>;

export const AnalyseTextResponseSchema = z.object({
  text: z.string(),
  tokens: z.array(AnalysedTokenSchema),
  code_switch_spans: z.array(CodeSwitchSpanSchema),
});
export type AnalyseTextResponse = z.infer<typeof AnalyseTextResponseSchema>;

export const NormalizeTextResponseSchema = z.object({
  text: z.string(),
  normalized: z.string(),
  token_type: z.string(),
});
export type NormalizeTextResponse = z.infer<typeof NormalizeTextResponseSchema>;
